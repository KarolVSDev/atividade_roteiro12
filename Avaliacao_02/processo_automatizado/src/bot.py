from pathlib import Path
import sys

APP_ROOT = Path(__file__).resolve().parents[1]
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from src.email_monitor import processar_emails


def main():

    print("Iniciando robô de atendimento...\n")

    processar_emails()

    print("\nRobô finalizado.")


if __name__ == "__main__":
    main()