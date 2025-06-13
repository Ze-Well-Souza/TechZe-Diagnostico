import yaml
import sys

try:
    print("Validando arquivo YAML...")
    with open('.github/workflows/ci.yml', 'r') as f:
        yaml_content = yaml.safe_load(f)
    print("✅ YAML válido!")
    sys.exit(0)
except Exception as e:
    print(f"❌ Erro ao validar YAML: {e}")
    sys.exit(1)