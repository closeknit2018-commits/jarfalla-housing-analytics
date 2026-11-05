-- Calculate annual population growth by DeSO area.
-- Only compare population with the previous calendar year.
-- Keep different geographical versions separate.

with population_with_previous_year as (

    select
        geography_version,
        region_code,
        reference_year,
        population,

        lag(reference_year) over (
            partition by geography_version, region_code
            order by reference_year
        ) as previous_reference_year,

        lag(population) over (
            partition by geography_version, region_code
            order by reference_year
        ) as lagged_population

    from {{ ref('int_scb__deso_population_by_year') }}

),

population_with_valid_previous_year as (

    select
        geography_version,
        region_code,
        reference_year,
        population,
        previous_reference_year,

        case
            when previous_reference_year = reference_year - 1
                then lagged_population
            else null
        end as previous_population

    from population_with_previous_year

),

population_growth as (

    select
        geography_version,
        region_code,
        reference_year,
        population,
        previous_reference_year,
        previous_population,

        population - previous_population
            as population_change,

        round(
            (
                (population - previous_population)::numeric
                / nullif(previous_population, 0)
            ) * 100,
            2
        ) as population_growth_percent

    from population_with_valid_previous_year

)

select *
from population_growth
