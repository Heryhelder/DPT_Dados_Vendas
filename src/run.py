if __name__ == "__main__":
    """
    Executa o pipeline ETL completo de ponta a ponta.

    Fluxo: extract → validate → prepare → analyze → store.
    """
    def main():
        from pipeline import run_pipeline

        run_pipeline()

    main()