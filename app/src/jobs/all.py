from src import jobs


def run() -> None:
    jobs.bronze.erp_orders.run()
    jobs.bronze.gateway_transactions.run()
    jobs.silver.erp_orders.run()
    jobs.silver.gateway_transactions.run()
    jobs.gold.recon_order_result.run()
    jobs.gold.agg_reconciliation_summary.run()


if __name__ == '__main__':
    run()
