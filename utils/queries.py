ALL_SKILLS = """
SELECT name
FROM skills
ORDER BY name
"""

MARKET_DEMAND = """
SELECT
    s.name,
    COUNT(*) AS demand_count
FROM job_openings jo
JOIN job_opening_skills jos
    ON jo.id = jos.job_opening_id
JOIN skills s
    ON s.id = jos.skill_id
GROUP BY s.name
"""

SKILL_GROWTH = """
SELECT
    s.name,

    SUM(
        CASE
            WHEN jo.created_at >= CURRENT_DATE - INTERVAL '30 days'
            THEN 1
            ELSE 0
        END
    ) AS recent_count,

    SUM(
        CASE
            WHEN jo.created_at >= CURRENT_DATE - INTERVAL '60 days'
             AND jo.created_at < CURRENT_DATE - INTERVAL '30 days'
            THEN 1
            ELSE 0
        END
    ) AS prev_count

FROM job_openings jo
JOIN job_opening_skills jos
    ON jo.id = jos.job_opening_id
JOIN skills s
    ON s.id = jos.skill_id

GROUP BY s.name
"""

SKILL_NETWORK = """
SELECT
    jo1.skill_id AS base_skill,
    jo2.skill_id AS related_skill,
    COUNT(*) AS freq
FROM job_opening_skills jo1
JOIN job_opening_skills jo2
    ON jo1.job_opening_id = jo2.job_opening_id
WHERE jo1.skill_id <> jo2.skill_id
GROUP BY
    jo1.skill_id,
    jo2.skill_id
"""

SKILL_ID_MAP = """
SELECT id, name
FROM skills
"""

COMPANY_SKILLS = """
SELECT
    jo.company_name,
    s.name
FROM job_openings jo
JOIN job_opening_skills jos
    ON jo.id = jos.job_opening_id
JOIN skills s
    ON s.id = jos.skill_id
"""

SKILL_TREND = """
SELECT
    DATE_TRUNC('month', jo.created_at) AS month,
    s.name,
    COUNT(*) AS skill_count
FROM job_openings jo
JOIN job_opening_skills jos
    ON jo.id = jos.job_opening_id
JOIN skills s
    ON s.id = jos.skill_id
WHERE jo.created_at IS NOT NULL
GROUP BY 1, 2
ORDER BY 1, 2
"""

EXPERIENCE_SKILL_COUNT = """
SELECT
    COALESCE(NULLIF(TRIM(jo.experience), ''), '미분류') AS experience,
    s.name,
    COUNT(*) AS skill_count
FROM job_openings jo
JOIN job_opening_skills jos
    ON jo.id = jos.job_opening_id
JOIN skills s
    ON s.id = jos.skill_id
GROUP BY 1, 2
ORDER BY 1, 2
"""