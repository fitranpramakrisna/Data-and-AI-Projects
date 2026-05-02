-- fact_salesorder
{{
  config(
    materialized='table'
  )
}}

SELECT 
  `Order ID` AS order_id, 
  Date AS date,
  Status AS status,
  {{ dbt_utils.generate_surrogate_key([
				'SKU'
			]) }} as product_id,
  {{ dbt_utils.generate_surrogate_key([
				'Fulfilment', 
				'`fulfilled-by`'
			])}} AS fulfillment_id,
  {{ dbt_utils.generate_surrogate_key([
				'`promotion-ids`'
			]) }} as promotion_id,
  {{ dbt_utils.generate_surrogate_key([
				'`ship-service-level`'
			]) }} as ship_service_id,
    {{ dbt_utils.generate_surrogate_key([
				'`Sales Channel `'
			]) }} as sales_channel_id,
  SUM(qty) AS qty,
  COALESCE(SUM(amount),0) AS amount,
FROM
    {{ source('bronze', 'amazon_sale_report') }}
GROUP BY ALL