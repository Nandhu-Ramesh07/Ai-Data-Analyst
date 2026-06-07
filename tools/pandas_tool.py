class PandasTool:

    @staticmethod
    def execute(code, df):

        try:

            result = eval(
                code,
                {
                    "df": df
                }
            )

            return str(result)

        except Exception as e:

            return f"Execution Error: {e}"