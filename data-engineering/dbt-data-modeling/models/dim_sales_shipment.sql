-- dim_sales_shipment
{{
config(
    materialized = 'table'
    )
}}

With t_data AS (
    SELECT DISTINCT 
    `ship-service-level` AS ship_service
    FROM {{ source ('bronze', 'amazon_sale_report')}}
)

SELECT {{ dbt_utils.generate_surrogate_key([
				'ship_service'
			]) }} as ship_service_id, *
FROM t_data