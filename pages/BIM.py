# -*- coding: utf-8 -*-
import base64
import time
import webbrowser
import requests
import pandas as pd
from urllib.parse import urlencode, urlparse, parse_qs
from datetime import datetime
from collections import defaultdict

# =========================================================
# 🔑 CREDENCIAIS DO TEU APP (conforme informado)
# =========================================================
CLIENT_ID = "OngD9h7cwfK7O8Qu0AucdCjR4FwRyNxg8vXPN4LYxc2MGQJw"
CLIENT_SECRET = "5Zq9pCS7Wp2Eh4UMdbLqJxmheJGtnRX4btIEOIpOhdle5Iic3ANbB5XqxPKyADXm"
REDIRECT_URI = "https://quanta-dashboard.onrender.com/" 

# Escopos possíveis sem Issues:
SCOPES = "data:read account:read"

# =========================================================
# ⚙️ Helpers
# =========================================================
SLEEP = 0.2  # para evitar throttling simples

def b64(s: str) -> str:
    return base64.urlsafe_b64encode(s.encode("utf-8")).decode("utf-8").rstrip("=")

def iso_parse(s):
    try:
        return datetime.fromisoformat(s.replace("Z","+00:00"))
    except Exception:
        return None

def safe_get(d, path, default=None):
    cur = d
    for p in path.split("."):
        if isinstance(cur, dict) and p in cur:
            cur = cur[p]
        else:
            return default
    return cur

# =========================================================
# 🔐 OAuth 3-legged
# =========================================================
def oauth_authorize_get_code():
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPES
    }
    auth_url = f"https://developer.api.autodesk.com/authentication/v2/authorize?{urlencode(params)}"
    print("\nAbra e autorize no navegador (login ACC). Copie o parâmetro 'code' da URL de retorno:")
    print(auth_url, "\n")
    webbrowser.open(auth_url)
    code = input("Cole aqui o 'code': ").strip()
    # Usuário às vezes cola a URL inteira; vamos extrair se necessário:
    if code.startswith("http"):
        parsed = urlparse(code)
        code_param = parse_qs(parsed.query).get("code", [""])[0]
        code = code_param or code
    return code

def oauth_get_access_token(auth_code):
    url = "https://developer.api.autodesk.com/authentication/v2/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": REDIRECT_URI
    }
    r = requests.post(url, headers=headers, data=payload)
    if r.status_code != 200:
        print("⚠️ Erro ao trocar code por token:", r.status_code, r.text)
        r.raise_for_status()
    tokens = r.json()
    print("✅ Access token obtido.")
    return tokens["access_token"]

# =========================================================
# 🗂️ Data Management — Hubs, Projetos, Pastas, Arquivos, Versões
# =========================================================
def dm_list_hubs(token):
    url = "https://developer.api.autodesk.com/project/v1/hubs"
    r = requests.get(url, headers={"Authorization": f"Bearer {token}"})
    r.raise_for_status()
    return r.json().get("data", [])

def dm_list_projects(token, hub_id):
    url = f"https://developer.api.autodesk.com/project/v1/hubs/{hub_id}/projects"
    r = requests.get(url, headers={"Authorization": f"Bearer {token}"})
    r.raise_for_status()
    return r.json().get("data", [])

def dm_top_folders(token, hub_id, project_id):
    url = f"https://developer.api.autodesk.com/project/v1/hubs/{hub_id}/projects/{project_id}/topFolders"
    r = requests.get(url, headers={"Authorization": f"Bearer {token}"})
    r.raise_for_status()
    return r.json().get("data", [])

def dm_folder_contents(token, project_id, folder_id):
    url = f"https://developer.api.autodesk.com/data/v1/projects/{project_id}/folders/{folder_id}/contents"
    r = requests.get(url, headers={"Authorization": f"Bearer {token}"})
    r.raise_for_status()
    return r.json().get("data", [])

def dm_item_versions(token, project_id, item_id):
    url = f"https://developer.api.autodesk.com/data/v1/projects/{project_id}/items/{item_id}/versions"
    r = requests.get(url, headers={"Authorization": f"Bearer {token}"})
    r.raise_for_status()
    return r.json().get("data", [])

# =========================================================
# 👥 ACC Project API — usuários por projeto (pode requerer integração habilitada)
# =========================================================
def acc_list_project_users(token, account_id, project_id):
    # Endpoint comum do ACC; pode retornar 403/404 caso a integração não esteja habilitada
    url = f"https://api.acc.autodesk.com/project/v1/accounts/{account_id}/projects/{project_id}/users"
    r = requests.get(url, headers={"Authorization": f"Bearer {token}"})
    if r.status_code != 200:
        # Retornamos vazio mas registramos motivo
        print(f"⚠️ Não foi possível listar usuários do projeto {project_id} (HTTP {r.status_code}): {r.text[:200]}")
        return []
    return r.json().get("results", []) or r.json().get("users", [])

# =========================================================
# 🧠 Model Derivative — propriedades do modelo
# =========================================================
def md_metadata(token, urn_b64):
    url = f"https://developer.api.autodesk.com/modelderivative/v2/designdata/{urn_b64}/metadata"
    r = requests.get(url, headers={"Authorization": f"Bearer {token}"})
    if r.status_code != 200:
        return None
    return r.json()

def md_properties(token, urn_b64, guid):
    url = f"https://developer.api.autodesk.com/modelderivative/v2/designdata/{urn_b64}/metadata/{guid}/properties"
    r = requests.get(url, headers={"Authorization": f"Bearer {token}"})
    if r.status_code != 200:
        return None
    return r.json()

# =========================================================
# 🔍 Varredura de projeto para métricas documentais e BIM
# =========================================================
def scan_project(token, hub, project):
    hub_id = hub["id"]
    project_id = project["id"]
    project_name = project["attributes"]["name"]

    # Top folders (vamos focar nos principais, incluindo containers ISO por nome)
    top = dm_top_folders(token, hub_id, project_id)
    top_map = {f["attributes"]["name"]: f for f in top}

    containers_iso = {"WIP":0, "Shared":0, "Published":0, "Archive":0}

    files_rows = []      # todos arquivos + versões
    versions_rows = []   # para cadência
    per_file_versions = []

    for f in top:
        if f["type"] != "folders": 
            continue
        stack = [f]
        while stack:
            node = stack.pop()
            time.sleep(SLEEP)
            contents = dm_folder_contents(token, project_id, node["id"])
            for c in contents:
                t = c["type"]
                if t == "folders":
                    stack.append(c)
                elif t == "items":
                    item_id = c["id"]
                    name = c["attributes"]["displayName"]
                    tip = safe_get(c, "relationships.tip.data.id")
                    # contamos container ISO por nome do top folder
                    top_name = f["attributes"]["name"]
                    if top_name in containers_iso:
                        containers_iso[top_name] += 1

                    time.sleep(SLEEP)
                    versions = dm_item_versions(token, project_id, item_id)
                    vcount = len(versions)
                    per_file_versions.append({
                        "hub_id": hub_id,
                        "project_id": project_id,
                        "project_name": project_name,
                        "item_id": item_id,
                        "file_name": name,
                        "versions": vcount
                    })

                    # Registrar cada versão (para cadência)
                    timestamps = []
                    for v in versions:
                        v_id = v["id"]
                        urn = safe_get(v, "relationships.derivatives.data.id") or v.get("id")
                        created = safe_get(v, "attributes.createTime") or safe_get(v, "attributes.lastModifiedTime")
                        timestamps.append((v_id, created, urn))
                        files_rows.append({
                            "hub_id": hub_id,
                            "project_id": project_id,
                            "project_name": project_name,
                            "item_id": item_id,
                            "file_name": name,
                            "version_id": v_id,
                            "created_at": created,
                            "derivative_urn": urn
                        })

                    # Cadência (diferença média entre versões)
                    if len(timestamps) >= 2:
                        ts_sorted = sorted([iso_parse(t[1]) for t in timestamps if t[1]], key=lambda x: x)
                        gaps = []
                        for i in range(1, len(ts_sorted)):
                            delta = (ts_sorted[i] - ts_sorted[i-1]).total_seconds()/3600.0  # horas
                            gaps.append(delta)
                        avg_gap_h = sum(gaps)/len(gaps) if gaps else None
                    else:
                        avg_gap_h = None

                    versions_rows.append({
                        "hub_id": hub_id,
                        "project_id": project_id,
                        "project_name": project_name,
                        "item_id": item_id,
                        "file_name": name,
                        "versions": vcount,
                        "avg_gap_hours": round(avg_gap_h,2) if avg_gap_h else None
                    })

    # Estatísticas de documentos
    df_files = pd.DataFrame(files_rows)
    df_versions = pd.DataFrame(versions_rows)
    df_perfile = pd.DataFrame(per_file_versions)

    # Top 10 mais revisados
    df_top10 = df_perfile.sort_values("versions", ascending=False).head(10)

    # Resumo por projeto
    total_files = len(df_perfile)
    total_versions = int(df_perfile["versions"].sum()) if not df_perfile.empty else 0
    users_count = None  # vamos tentar pela ACC API abaixo

    # Tenta descobrir account_id a partir do hub_id (formato comum: 'b.{account_guid}')
    account_id = hub_id.split(".")[-1] if "." in hub_id else None
    if account_id:
        users = acc_list_project_users(token, account_id, project_id)
        users_count = len(users) if users else None
        # salvar detalhamento de usuários (se existir)
        if users:
            pd.DataFrame(users).to_csv(f"users_{project_name}_{project_id}.csv", index=False, encoding="utf-8-sig")

    project_summary = {
        "hub_id": hub_id,
        "project_id": project_id,
        "project_name": project_name,
        "total_files": total_files,
        "total_versions": total_versions,
        "users_count": users_count,
        "wip_files": containers_iso["WIP"],
        "shared_files": containers_iso["Shared"],
        "published_files": containers_iso["Published"],
        "archive_files": containers_iso["Archive"]
    }

    return project_summary, df_files, df_perfile, df_top10, df_versions

# =========================================================
# 🧾 Model Derivative — propriedades (amostra por projeto)
# =========================================================
def extract_model_properties_sample(token, df_files, project_name, project_id, max_models=3):
    # Seleciona até N arquivos que aparentam ser modelos (por extensão no nome)
    candidates = df_files[df_files["file_name"].str.lower().str.endswith((".rvt",".ifc",".nwd",".nwc",".dwg",".dgn"), na=False)]
    if candidates.empty:
        return pd.DataFrame(), pd.DataFrame()

    # Pegamos o último version_id por item
    latest_by_item = candidates.sort_values("created_at").groupby("item_id").tail(1)
    sample = latest_by_item.tail(max_models)

    props_rows = []
    class_audit_rows = []
    for _, row in sample.iterrows():
        urn = row.get("derivative_urn") or row.get("version_id")
        if not urn:
            continue
        urn_b64 = b64(urn)

        meta = md_metadata(token, urn_b64)
        if not meta or "data" not in meta:
            continue

        # Normalmente o primeiro guid é o view principal
        guid = safe_get(meta, "data.metadata.0.guid")
        if not guid:
            continue

        props = md_properties(token, urn_b64, guid)
        if not props:
            continue

        # Estrutura comum: props["data"]["collections"][..]["properties"] com objetos
        # Vamos varrer e extrair alguns campos usuais
        objects = safe_get(props, "data.collection") or safe_get(props, "data.objects") or []
        for obj in objects:
            # Cada obj pode ter "properties" agrupadas por "Category", "Identity Data", etc.
            pmap = {}
            for grp_name, grp_vals in obj.get("properties", {}).items():
                for k, v in grp_vals.items():
                    key = f"{grp_name}.{k}"
                    pmap[key] = v

            cat = pmap.get("Item.Category") or pmap.get("Identity Data.Category") or pmap.get("Constraints.Category")
            fam = pmap.get("Item.Family") or pmap.get("Identity Data.Family")
            type_name = pmap.get("Item.Type Name") or pmap.get("Identity Data.Type Name")

            # Classificação (vários nomes possíveis)
            cls = (
                pmap.get("Identity Data.Uniclass") or
                pmap.get("Identity Data.OmniClass Number") or
                pmap.get("Classification.Code") or
                pmap.get("Classification.Uniformat")
            )
            has_class = cls is not None and str(cls).strip() != ""

            props_rows.append({
                "project_id": project_id,
                "project_name": project_name,
                "item_id": row["item_id"],
                "file_name": row["file_name"],
                "category": cat,
                "family": fam,
                "type_name": type_name,
                "has_classification": has_class,
                "classification_value": cls
            })

            class_audit_rows.append({
                "project_id": project_id,
                "project_name": project_name,
                "file_name": row["file_name"],
                "element_has_classification": has_class
            })

    df_props = pd.DataFrame(props_rows)
    df_class = pd.DataFrame(class_audit_rows)
    return df_props, df_class

if __name__ == "__main__":
    try:
        print("=== OAuth 3-legged (data:read + account:read) ===")
        code = oauth_authorize_get_code()
        token = oauth_get_access_token(code)

        print("\n=== Listando hubs e projetos ===")
        hubs = dm_list_hubs(token)
        projects_summary = []
        all_files = []
        all_perfile = []
        all_top10 = []
        all_versions = []
        all_props = []
        all_class_audit = []

        for hub in hubs:
            hub_id = hub["id"]
            hub_name = hub["attributes"]["name"]
            time.sleep(SLEEP)
            projects = dm_list_projects(token, hub_id)
            if not projects:
                continue

            for proj in projects:
                pname = proj["attributes"]["name"]
                print(f"→ Varredura do projeto: {pname}")
                time.sleep(SLEEP)
                summary, df_files, df_perfile, df_top10, df_versions = scan_project(token, hub, proj)

                # salvar agregados
                projects_summary.append(summary)
                all_files.append(df_files)
                all_perfile.append(df_perfile)
                all_top10.append(df_top10.assign(project_name=summary["project_name"]))
                all_versions.append(df_versions)

                # Auditoria de propriedades BIM (amostra)
                if not df_files.empty:
                    dfp, dfc = extract_model_properties_sample(token, df_files, summary["project_name"], summary["project_id"])
                    if not dfp.empty: all_props.append(dfp)
                    if not dfc.empty: all_class_audit.append(dfc)

        # ======== Salvar relatórios ========
        df_projects = pd.DataFrame(projects_summary).sort_values("project_name") if projects_summary else pd.DataFrame()
        df_files_all = pd.concat(all_files, ignore_index=True) if all_files else pd.DataFrame()
        df_perfile_all = pd.concat(all_perfile, ignore_index=True) if all_perfile else pd.DataFrame()
        df_top10_all = pd.concat(all_top10, ignore_index=True) if all_top10 else pd.DataFrame()
        df_versions_all = pd.concat(all_versions, ignore_index=True) if all_versions else pd.DataFrame()
        df_props_all = pd.concat(all_props, ignore_index=True) if all_props else pd.DataFrame()
        df_class_all = pd.concat(all_class_audit, ignore_index=True) if all_class_audit else pd.DataFrame()

        # Dashboard de Governança
        if not df_projects.empty:
            df_projects.to_csv("governanca_projetos.csv", index=False, encoding="utf-8-sig")
            print("✅ governanca_projetos.csv gerado.")
        else:
            print("⚠️ Nenhum projeto encontrado (verifique permissões/integração).")

        # Controle Documental
        if not df_perfile_all.empty:
            df_perfile_all.to_csv("docs_por_arquivo.csv", index=False, encoding="utf-8-sig")
            print("✅ docs_por_arquivo.csv (versões por arquivo).")
        if not df_top10_all.empty:
            df_top10_all.to_csv("top10_mais_revisados.csv", index=False, encoding="utf-8-sig")
            print("✅ top10_mais_revisados.csv.")
        if not df_versions_all.empty:
            df_versions_all.to_csv("cadencia_uploads.csv", index=False, encoding="utf-8-sig")
            print("✅ cadencia_uploads.csv (média horas entre versões).")
        if not df_files_all.empty:
            # indicadores por containers ISO (contagem por projeto)
            iso_cols = ["project_id","project_name","wip_files","shared_files","published_files","archive_files"]
            if not df_projects.empty:
                df_projects[iso_cols].to_csv("iso19650_containers.csv", index=False, encoding="utf-8-sig")
                print("✅ iso19650_containers.csv.")

        # Auditoria de Modelos BIM
        if not df_props_all.empty:
            # Quantitativos simples
            df_props_all.to_csv("model_properties_sample.csv", index=False, encoding="utf-8-sig")
            q1 = df_props_all.groupby(["project_name","category"]).size().reset_index(name="count")
            q1.to_csv("quantitativos_por_categoria.csv", index=False, encoding="utf-8-sig")
            print("✅ model_properties_sample.csv e quantitativos_por_categoria.csv.")
        if not df_class_all.empty:
            class_rate = df_props_all.groupby("project_name")["has_classification"].mean().reset_index()
            class_rate.rename(columns={"has_classification":"classification_ratio"}, inplace=True)
            class_rate.to_csv("auditoria_classificacao.csv", index=False, encoding="utf-8-sig")
            print("✅ auditoria_classificacao.csv.")

        print("\n🏁 Concluído. Se algum CSV não apareceu, o motivo foi logado acima (permissões/integração).")

    except Exception as e:
        print("❌ Erro fatal:", e)
