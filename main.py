# main.py
"""
Este script foi desenvolvido exclusivamente para fins de estudo e aprendizado.
Todos os dados coletados são provenientes da API pública do YouTube e são utilizados
de acordo com os termos de uso da plataforma. Não há intenção comercial ou violação
de direitos autorais."""

# Importação de bibliotecas
import os
from googleapiclient.discovery import build
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

API_KEY = "SUA_API_KEY_AQUI" #coloque sua chave
youtube = build('youtube', 'v3', developerKey=API_KEY)

# Buscar pelo nome do canal
request = youtube.search().list(
    q="NOME",
    part="snippet",
    type="channel",
    maxResults=1
)
response = request.execute()
channel_id = response['items'][0]['snippet']['channelId']
print("ID do Canal:", channel_id)


### Obtendo a Playlist de Uploads do Canal
# Função para obter a playlist de uploads do canal
def get_uploads_playlist_id(channel_id):
    try:
        response = youtube.channels().list(
            id=channel_id,
            part='contentDetails'
        ).execute()

        if 'items' in response and len(response['items']) > 0:
            return response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        else:
            print(f"Canal {channel_id} não tem uploads ou não foi encontrado.")
            return None    
    except Exception as e:
        print(f"Erro ao obter playlist: {str(e)}")
        return None

### Coletando os Vídeos da Playlist
# Função para coletar todos os vídeos da playlist
def get_all_videos(playlist_id):
    videos = []
    next_page_token = None
    
    try:
        while True:
            response = youtube.playlistItems().list(
                playlistId=playlist_id,
                part="snippet",
                maxResults=50,
                pageToken=next_page_token
            ).execute()
            
            for item in response['items']:
                video_id = item['snippet']['resourceId']['videoId']
                videos.append({
                    'video_id': video_id,
                    'title': item['snippet']['title'],
                    'published_at': item['snippet']['publishedAt']
                })
            
            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break

        print(f"{len(videos)} vídeos coletados.")
    except Exception as e:
        print(f"Erro na coleta de vídeos: {str(e)}")
    
    return videos

### Coletando as Estatísticas dos Vídeos
# Função para obter estatísticas dos vídeos
def get_video_stats(video_ids):
    stats = []
    
    try:
        for i in range(0, len(video_ids), 50):
            chunk = video_ids[i:i+50]
            response = youtube.videos().list(
                part="statistics,snippet",
                id=','.join(chunk)
            ).execute()

            if 'items' in response:
                for item in response['items']:
                    stat = item['statistics']
                    stats.append({
                        'title': item['snippet']['title'],
                        'video_id': item['id'],
                        'views': int(stat.get('viewCount', 0)),
                        'likes': int(stat.get('likeCount', 0)),
                        'comment_count': int(stat.get('commentCount', 0)),
                        'published_at': item['snippet']['publishedAt']
                    })
            else:
                print("Nenhum dado encontrado para os vídeos.")
                                
    except Exception as e:
        print(f"Erro na coleta de estatísticas: {str(e)}")
    
    return stats


### Processamento e Salvamento em CSV
# Processamento principal
def main(channel_id):
    # Obter playlist de uploads
    playlist_id = get_uploads_playlist_id(channel_id)
    if not playlist_id:
        return
    
    # Coletar vídeos
    videos = get_all_videos(playlist_id)
    print(f"Vídeos encontrados: {len(videos)}")
    
    # Coletar estatísticas
    video_ids = [v['video_id'] for v in videos]
    stats = get_video_stats(video_ids)
    
    # Criar DataFrame
    df = pd.DataFrame(stats)
    
    # Processar datas
    df['published_at'] = pd.to_datetime(df['published_at'])
    df['data'] = df['published_at'].dt.date
    df['hora'] = df['published_at'].dt.time
    
    # Ordenar por data
    df = df.sort_values('published_at')
    
    # Salvar em CSV
    df.to_csv('NOME_youtube_stats.csv', index=False)
    return df



# Execução
if __name__ == "__main__":
    # ID do canal desejado
    CHANNEL_ID = 'ID_CANAL'  # Substitua pelo ID do canal desejado
    
    df = main(CHANNEL_ID)
    if df is not None:
        print("\nPrimeiras linhas do DataFrame:")
        print(df.head())
