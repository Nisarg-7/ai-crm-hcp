from app.core.database import Base, engine
import app.models  # noqa: F401  (registers all models on Base)


def main():
    Base.metadata.create_all(bind=engine)
    print("Tables created:", sorted(Base.metadata.tables.keys()))


if __name__ == "__main__":
    main()