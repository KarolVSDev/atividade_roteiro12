from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import os
import pickle

SCOPES = [
    "https://www.googleapis.com/auth/drive"
]

# IDs das pastas principais
PASTA_DOCUMENTOS_OK = "1bsTPbIwscXfwFdlk7Nf4_5CvtaOqsoXU"
PASTA_DOCUMENTOS_PENDENTES = "1Hz8VRIPzTWHS5CjXwb9BrE7Ev5wALW9P"
PASTA_ENCAMINHADOS = "1_MDTTzM00RNQz7MhT0GrZjmh8ILQR_N8"
PASTA_DRIVE_DOWNLOAD = "1dMZwGTF3X_45AgDZ2yd3dWO5TTlWhu3-"
PASTA_DOWNLOAD = "downloads"



def autenticar_google_drive():

    creds = None

    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "client_secret.json",
                SCOPES
            )

            creds = flow.run_local_server(port=0)

        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    return build(
        "drive",
        "v3",
        credentials=creds
    )


def upload_arquivo(
    service,
    caminho_arquivo,
    pasta_id
):
    metadata = {
        "name": os.path.basename(caminho_arquivo),
        "parents": [pasta_id]
    }

    media = MediaFileUpload(
        caminho_arquivo,
        resumable=True
    )

    arquivo = service.files().create(
        body=metadata,
        media_body=media,
        fields="id,name"
    ).execute()

    print(
        f"Upload realizado: {arquivo['name']} na pasta ID: {pasta_id}"
    )
    return arquivo["id"]

def criar_subpasta(
    service,
    nome_cliente,
    pasta_pai_id
):

    query = (
        f"name='{nome_cliente}' "
        f"and '{pasta_pai_id}' in parents "
        "and mimeType='application/vnd.google-apps.folder' "
        "and trashed=false"
    )

    resultado = service.files().list(
        q=query,
        fields="files(id,name,parents)"
    ).execute()

    pastas = resultado.get(
        "files",
        []
    )

    if pastas:

        pasta_id = pastas[0]["id"]

        print(
            f"Pasta já existente: {nome_cliente}"
        )

        print(
            f"ID da pasta: {pasta_id}"
        )

        print(
            f"Pasta pai: {pasta_pai_id}"
        )

        return pasta_id

    metadata = {
        "name": nome_cliente,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [pasta_pai_id]
    }

    pasta = service.files().create(
        body=metadata,
        fields="id,name,parents"
    ).execute()

    print(
        f"Pasta criada: {pasta['name']}"
    )

    print(
        f"ID da pasta criada: {pasta['id']}"
    )

    print(
        f"Pasta pai: {pasta_pai_id}"
    )

    return pasta["id"]

def mover_arquivo(
    service,
    arquivo_id,
    nova_pasta_id
):

    arquivo = service.files().get(
        fileId=arquivo_id,
        fields="id,name,parents"
    ).execute()

    pais_atuais = arquivo.get(
        "parents",
        []
    )

    resultado = service.files().update(
        fileId=arquivo_id,
        addParents=nova_pasta_id,
        removeParents=",".join(pais_atuais),
        fields="id,name,parents"
    ).execute()

    # print(
    #     f"Arquivo movido: {resultado['name']}"
    # )

    # print(
    #     f"Novo pai: {nova_pasta_id}"
    # )

    # print(
    #     f"Parents atuais: {resultado.get('parents', [])}"
    # )

    return resultado