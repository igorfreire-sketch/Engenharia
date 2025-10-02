import toml
import os

secrets_path = ".streamlit/secrets.toml"

print(f"--- Testando o arquivo em: {secrets_path} ---")

if not os.path.exists(secrets_path):
    print("\nERRO CRÍTICO: O arquivo secrets.toml NÃO FOI ENCONTRADO no caminho esperado.")
    print("Verifique se a pasta '.streamlit' e o arquivo 'secrets.toml' existem na raiz do seu projeto.")
else:
    print("\nSUCESSO: Arquivo encontrado!")
    
    try:
        with open(secrets_path, "r", encoding="utf-8") as f:
            data = toml.load(f)
        
        print("\nSUCESSO: O arquivo foi lido e decodificado sem erros.")
        print("\n--- Conteúdo Lido do Arquivo ---")
        print(data)
        print("---------------------------------")
        if "master_email_list" in data:
            print("\nSUCESSO: A chave 'master_email_list' foi encontrada no nível principal do arquivo.")
            print(f"Valor: {data['master_email_list']}")
        else:
            print("\nERRO: A chave 'master_email_list' NÃO foi encontrada no nível principal do arquivo.")
            if "email_credentials" in data and "master_email_list" in data["email_credentials"]:
                print("Causa provável: A lista de e-mails ainda está DENTRO da seção [email_credentials].")

    except toml.TomlDecodeError as e:
        print(f"\nERRO CRÍTICO: O arquivo secrets.toml está mal formatado ou contém caracteres inválidos.")
        print("O leitor TOML falhou com o seguinte erro:")
        print(f"  -> {e}")
        print("\nSOLUÇÃO: Recrie o arquivo do zero, copiando o modelo limpo da minha resposta anterior.")
    except Exception as e:
        print(f"\nOcorreu um erro inesperado: {e}")