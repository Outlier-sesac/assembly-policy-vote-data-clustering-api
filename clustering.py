import pyodbc
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import LabelEncoder

def get_db_connection():
    return pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=outliers.database.windows.net;"
        "DATABASE=outliers_database;"
        "UID=outliers_admin;"
        "PWD=ZBofe3XjbLeVpr7HfPah;"
        "TrustServerCertificate=yes;"
    )

def run_clustering_from_db():
    query = """
    SELECT 
        ar.MEMBER_NO,
        ar.HG_NM,
        ar.POLY_NM,
        ar.BILL_NO,
        ar.RESULT_VOTE_MOD
    FROM assembly_plenary_session_vote ar
    WHERE ar.RESULT_VOTE_MOD IS NOT NULL
    """

    conn = get_db_connection()
    df = pd.read_sql(query, conn)
    conn.close()

    # 피벗 테이블 생성
    vote_matrix = df.pivot_table(
        index='MEMBER_NO',
        columns='BILL_NO',
        values='RESULT_VOTE_MOD',
        aggfunc='first'
    ).fillna('미투표')

    le = LabelEncoder()
    vote_matrix_encoded = vote_matrix.apply(le.fit_transform)

    # 클러스터링
    kmeans = KMeans(n_clusters=3, random_state=42)
    clusters = kmeans.fit_predict(vote_matrix_encoded)

    # 차원 축소
    pca = PCA(n_components=2)
    coordinates = pca.fit_transform(vote_matrix_encoded)

    # 좌표 정규화 (0~1 범위로)
    scaler = MinMaxScaler()
    coordinates_scaled = scaler.fit_transform(coordinates)

    # 의원 정보
    member_info = df[['MEMBER_NO', 'HG_NM', 'POLY_NM']].drop_duplicates().set_index('MEMBER_NO')

    results = []
    for i, member_no in enumerate(vote_matrix.index):
        member = member_info.loc[member_no]
        results.append({
            "member_id": str(member_no),
            "member_name": member['HG_NM'],
            "party": member['POLY_NM'],
            "cluster": int(clusters[i]),
            "coordinates": [float(coordinates[i][0]), float(coordinates[i][1])],
            "similarity": 0.0
        })
    return results
