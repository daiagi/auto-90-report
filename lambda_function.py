from src.main import main

def handler(event, context):
    main()
    DATA_DIR = Path(__file__).resolve()
    return 'Hello from AWS Lambda using Python' + f"{DATA_DIR}" + '!'



