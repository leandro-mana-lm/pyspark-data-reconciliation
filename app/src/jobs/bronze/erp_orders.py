import stagefy
from src import layers
from stagefy.connections import SparkConnection
from stagefy.interfaces import IDataQuery


def run() -> None:
    config = {'spark.sql.session.timeZone': 'America/Sao_Paulo'}

    connection = SparkConnection(config=config)

    parameters: list[IDataQuery] = [
        layers.bronze.ErpOrders(),
    ]

    process = stagefy.Process(
        connection=connection,
        parameters=parameters,
    )

    process.run()


if __name__ == '__main__':
    run()
