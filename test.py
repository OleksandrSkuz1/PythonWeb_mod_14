try:
    import src.main
    import src.repository.contacts
    import src.repository.users
    import src.routes.contacts
    import src.routes.users
    import src.routes.auth
    import src.services.auth
    import src.services.email
    print("Imports successful!")
except ImportError as e:
    print(f"Import failed: {e}")
