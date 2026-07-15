import threading
import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import svds
import psycopg2
from django.conf import settings
from django.db.models import Avg, Count, Prefetch
from product.models import Product, ProductVariant

class CollaborativeRecommender:
    def __init__(self, latent_factors=15):
        self.latent_factors = latent_factors
        self.user_item_matrix = None
        self.U = None
        self.sigma_diag = None
        self.Vt = None
        self.user_to_idx = {}
        self.item_to_idx = {}
        self.idx_to_item = {}

    def fit(self, interactions_df: pd.DataFrame):
        """
        Builds the user-item interaction matrix and calculates SVD factors.
        interactions_df: DataFrame with columns ['customer_id', 'item_id', 'order_count']
        """
        self.user_item_matrix = interactions_df.pivot(
            index='customer_id', 
            columns='item_id', 
            values='order_count'
        ).fillna(0)
        
        self.user_to_idx = {user_id: idx for idx, user_id in enumerate(self.user_item_matrix.index)}
        self.item_to_idx = {item_id: idx for idx, item_id in enumerate(self.user_item_matrix.columns)}
        self.idx_to_item = {idx: item_id for item_id, idx in self.item_to_idx.items()}
        
        sparse_matrix = csr_matrix(self.user_item_matrix.values)
        num_users, num_items = sparse_matrix.shape
        k = min(self.latent_factors, num_users - 1, num_items - 1)
        
        if k > 0:
            U, sigma, Vt = svds(sparse_matrix, k=k)
            self.U = U
            self.sigma_diag = np.diag(sigma)
            self.Vt = Vt
        else:
            self.U = None
            self.sigma_diag = None
            self.Vt = None

    def recommend(self, user_id, k=5, exclude_ordered=True) -> list[tuple[str, float]]:
        """
        Recommends top-k items for user_id.
        Returns a list of tuples: (item_id, predicted_score)
        """
        if self.user_item_matrix is None or user_id not in self.user_to_idx:
            return []
            
        u_idx = self.user_to_idx[user_id]
        
        if self.U is not None and self.sigma_diag is not None and self.Vt is not None:
            predicted_ratings = np.dot(np.dot(self.U[u_idx, :], self.sigma_diag), self.Vt)
        else:
            predicted_ratings = self.user_item_matrix.mean(axis=0).values
            
        user_history = self.user_item_matrix.loc[user_id]
        already_ordered = set(user_history[user_history > 0].index) if exclude_ordered else set()
        
        scores = {}
        for item_id, idx in self.item_to_idx.items():
            if item_id in already_ordered:
                continue
            scores[item_id] = float(predicted_ratings[idx])
            
        recommended = sorted(
            [(item_id, score) for item_id, score in scores.items() if score > 0], 
            key=lambda x: x[1], 
            reverse=True
        )
        
        if k is not None:
            recommended = recommended[:k]
            
        return recommended


class ContentBasedRecommender:
    def __init__(self):
        self.menu_embeddings = {}
        
    def fit(self, conn):
        """Loads all menu embeddings from Postgres into memory."""
        self.menu_embeddings = {}
        with conn.cursor() as cur:
            cur.execute("SELECT item_id::text, embedding::text FROM ml.menu_embeddings")
            for item_id, emb_str in cur.fetchall():
                self.menu_embeddings[item_id] = np.array([float(x) for x in emb_str.strip('[]').split(',')])

    def recommend(self, user_id, user_history_df, k=5, exclude_ordered=True) -> list[tuple[str, float]]:
        """
        Creates a weighted user profile vector, compares it against candidate 
        item embeddings using cosine similarity, and returns the top k.
        """
        user_history = user_history_df[user_history_df['customer_id'] == user_id]
        if user_history.empty:
            return []
            
        weighted_vectors = []
        total_weights = 0
        already_ordered = set()
        
        for _, row in user_history.iterrows():
            item_id = row['item_id']
            count = row['order_count']
            already_ordered.add(item_id)
            
            if item_id in self.menu_embeddings:
                weighted_vectors.append(self.menu_embeddings[item_id] * count)
                total_weights += count
                
        if total_weights == 0:
            return []
            
        user_profile = sum(weighted_vectors) / total_weights
        
        exclude_set = already_ordered if exclude_ordered else set()
        
        scores = {}
        for item_id, item_vector in self.menu_embeddings.items():
            if item_id in exclude_set:
                continue
                
            dot_product = np.dot(user_profile, item_vector)
            norm_profile = np.linalg.norm(user_profile)
            norm_item = np.linalg.norm(item_vector)
            
            if norm_profile > 0 and norm_item > 0:
                similarity = dot_product / (norm_profile * norm_item)
                scores[item_id] = float(similarity)
            else:
                scores[item_id] = 0.0
                
        recommended = sorted(
            [(item_id, score) for item_id, score in scores.items() if score > 0],
            key=lambda x: x[1],
            reverse=True
        )
        
        if k is not None:
            recommended = recommended[:k]
            
        return recommended


class HybridRecommender:
    def __init__(self, cf_recommender, content_recommender, alpha=0.7):
        self.cf_recommender = cf_recommender
        self.content_recommender = content_recommender
        self.alpha = alpha
        
    def recommend(self, user_id, user_history_df, k=5, exclude_ordered=True) -> list[tuple[str, float]]:
        """
        Retrieves raw scores from both models, applies Min-Max normalization,
        and computes the blended hybrid score: alpha * CF + (1 - alpha) * Content.
        """
        cf_recs = self.cf_recommender.recommend(user_id, k=None, exclude_ordered=exclude_ordered)
        content_recs = self.content_recommender.recommend(user_id, user_history_df, k=None, exclude_ordered=exclude_ordered)
        
        if not cf_recs and not content_recs:
            return []
            
        cf_dict = dict(cf_recs)
        content_dict = dict(content_recs)
        
        all_candidates = set(cf_dict.keys()).union(set(content_dict.keys()))
        
        def normalize(scores_dict):
            if not scores_dict:
                return {}
            vals = list(scores_dict.values())
            min_val, max_val = min(vals), max(vals)
            val_range = max_val - min_val
            if val_range == 0:
                return {item: 1.0 for item in scores_dict}
            return {item: (val - min_val) / val_range for item, val in scores_dict.items()}
            
        norm_cf = normalize(cf_dict)
        norm_content = normalize(content_dict)
        
        hybrid_scores = {}
        for item_id in all_candidates:
            cf_val = norm_cf.get(item_id, 0.0)
            content_val = norm_content.get(item_id, 0.0)
            
            hybrid_scores[item_id] = self.alpha * cf_val + (1.0 - self.alpha) * content_val
            
        recommended = sorted(
            [(item_id, score) for item_id, score in hybrid_scores.items() if score > 0],
            key=lambda x: x[1],
            reverse=True
        )
        
        if k is not None:
            recommended = recommended[:k]
            
        return recommended


_cf_recommender = None
_content_recommender = None
_hybrid_recommender = None
_interactions_df = None
_recommender_lock = threading.Lock()

def get_recommenders():
    global _cf_recommender, _content_recommender, _hybrid_recommender, _interactions_df
    if _cf_recommender is None:
        with _recommender_lock:
            if _cf_recommender is None:
                db_config = settings.DATABASES['default']
                conn = psycopg2.connect(
                    dbname=db_config['NAME'],
                    user=db_config['USER'],
                    password=db_config['PASSWORD'],
                    host=db_config['HOST'],
                    port=db_config['PORT']
                )
                try:
                    cutoff_date = "2027-04-26 00:00:00"
                    query = """
                        SELECT 
                            customer_id::text, 
                            COALESCE(product_id, item_id)::text AS item_id, 
                            COUNT(*) AS order_count
                        FROM ml.analytics_view
                        WHERE order_created_at < %s
                        GROUP BY customer_id, COALESCE(product_id, item_id);
                    """
                    df = pd.read_sql(query, conn, params=(cutoff_date,))
                    _interactions_df = df
                    
                    cf = CollaborativeRecommender(latent_factors=15)
                    cf.fit(df)
                    
                    content = ContentBasedRecommender()
                    content.fit(conn)
                    
                    hybrid = HybridRecommender(cf, content, alpha=0.7)
                    
                    _cf_recommender = cf
                    _content_recommender = content
                    _hybrid_recommender = hybrid
                finally:
                    conn.close()
    return _cf_recommender, _content_recommender, _hybrid_recommender, _interactions_df


def get_popular_products(k=5, exclude_ids=None):
    """
    Returns top ordered products as fallback/padding, using cached dataframe to avoid slow database joins.
    """
    cf, content, hybrid, df = get_recommenders()
    
    # Calculate item popularity from loaded dataframe
    item_popularity = df.groupby('item_id')['order_count'].sum()
    popular_ids = item_popularity.sort_values(ascending=False).index.tolist()
    
    if exclude_ids:
        popular_ids = [pid for pid in popular_ids if pid not in exclude_ids]
        
    target_ids = popular_ids[:k]
    
    valid_variants = ProductVariant.objects.filter(is_thali_component=False)
    products = Product.objects.filter(
        id__in=target_ids,
        is_active=True,
        variants__is_thali_component=False
    ).prefetch_related(
        Prefetch("variants", queryset=valid_variants), "images"
    ).annotate(
        average_rating=Avg("ratings__rating"),
        rating_count=Count("ratings", distinct=True)
    )
    
    products_list = list(products)
    products_list.sort(key=lambda p: target_ids.index(str(p.id)) if str(p.id) in target_ids else 999)
    
    if len(products_list) < k:
        needed = k - len(products_list)
        fallback = Product.objects.filter(
            is_active=True,
            variants__is_thali_component=False
        ).prefetch_related(
            Prefetch("variants", queryset=valid_variants), "images"
        ).annotate(
            average_rating=Avg("ratings__rating"),
            rating_count=Count("ratings", distinct=True)
        )[:needed]
        products_list.extend(list(fallback))
        
    return products_list[:k]


def get_hybrid_recommendations(user_id, k=5, alpha=0.7, exclude_ordered=True):
    """
    Retrieves hybrid recommendations for user_id, fallback/pad to popular products.
    """
    cf, content, hybrid, df = get_recommenders()
    
    if alpha != hybrid.alpha:
        hybrid_rec = HybridRecommender(cf, content, alpha=alpha)
    else:
        hybrid_rec = hybrid
        
    recs = hybrid_rec.recommend(str(user_id), df, k=k, exclude_ordered=exclude_ordered)
    recommended_product_ids = [item_id for item_id, score in recs]
    
    if not recommended_product_ids:
        return get_popular_products(k)
        
    valid_variants = ProductVariant.objects.filter(is_thali_component=False)
    products = Product.objects.filter(
        id__in=recommended_product_ids,
        is_active=True,
        variants__is_thali_component=False
    ).distinct().prefetch_related(
        Prefetch("variants", queryset=valid_variants), "images"
    ).annotate(
        average_rating=Avg("ratings__rating"),
        rating_count=Count("ratings", distinct=True)
    )
    
    products_list = list(products)
    products_list.sort(key=lambda p: recommended_product_ids.index(str(p.id)) if str(p.id) in recommended_product_ids else 999)
    
    if len(products_list) < k:
        needed = k - len(products_list)
        exclude_ids = [str(p.id) for p in products_list]
        popular = get_popular_products(needed, exclude_ids=exclude_ids)
        products_list.extend(popular)
        
    return products_list[:k]


def get_collaborative_recommendations(user_id, k=5):
    """
    Wrapper for backward compatibility.
    """
    return get_hybrid_recommendations(user_id, k=k)
