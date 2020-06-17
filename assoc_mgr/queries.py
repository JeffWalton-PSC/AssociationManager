import pandas as pd


def students(now, one_year_ago, connection):
    sql_str = f"""
    SELECT DISTINCT 
        P.PEOPLE_CODE_ID, 
        P.LAST_NAME, 
        P.FIRST_NAME, 
--      (P.LAST_NAME || ', ' || P.FIRST_NAME || ', ' || P.PEOPLE_CODE_ID) as STUDENT
        CONCAT(P.LAST_NAME, ', ' , P.FIRST_NAME, ', ' , P.PEOPLE_CODE_ID) as STUDENT
    FROM ACADEMIC as A inner join PEOPLE as P 
        ON A.PEOPLE_ID = P.PEOPLE_ID
    WHERE A.PRIMARY_FLAG = 'Y' 
        AND A.CURRICULUM NOT IN ('ADVST') 
        AND A.GRADUATED NOT IN ('G') 
        AND A.ACADEMIC_YEAR >= {one_year_ago} 
        AND A.ACADEMIC_YEAR <= {now}
    ORDER BY STUDENT
	"""
    return pd.read_sql_query(sql_str, connection)


def associations(connection):
    sql_str = f"""
	SELECT DISTINCT 
		C.CODE_VALUE as ASSOCIATION,
--		C.LONG_DESC || '-' || C.CODE_VALUE as ASSOC_LABEL
		CONCAT(C.LONG_DESC, '-', C.CODE_VALUE) as ASSOC_LABEL
	FROM CODE_ASSOCIATION AS C 
	WHERE C.STATUS = 'A'
	ORDER BY ASSOC_LABEL
	"""
    return pd.read_sql_query(sql_str, connection)


def yearterms(connection):
    sql_str = f"""
    SELECT DISTINCT
        ACADEMIC_YEAR,
        ACADEMIC_TERM,
        FINAL_END_DATE as END_DATE,
--      T.ACADEMIC_YEAR || '.' || T.ACADEMIC_TERM as YEARTERM
        CONCAT(T.ACADEMIC_YEAR, '.', T.ACADEMIC_TERM) as YEARTERM
    FROM   ACADEMICCALENDAR AS T
    WHERE  EXISTS(
            SELECT 1
            FROM ACADEMICCALENDAR
            WHERE ACADEMIC_YEAR = T.ACADEMIC_YEAR
                AND ACADEMIC_TERM = T.ACADEMIC_TERM
            GROUP BY ACADEMIC_YEAR, ACADEMIC_TERM
            HAVING T.FINAL_END_DATE = MAX(FINAL_END_DATE)
            )
            AND ACADEMIC_YEAR>=2015
            AND ACADEMIC_TERM in ('SPRING', 'SUMMER', 'FALL')
    ORDER BY END_DATE DESC
	"""
    return pd.read_sql_query(sql_str, connection)


def association_members(year, term, association, connection):
    sql_str = f"""
	SELECT DISTINCT
		PEOPLE_ORG_CODE_ID
	--	, ASSOCIATION
	--	, ACADEMIC_YEAR
	--	, ACADEMIC_TERM
	FROM ASSOCIATION
	WHERE ACADEMIC_YEAR = '{year}'
	and ACADEMIC_TERM = '{term}'
	and ASSOCIATION = '{association}'
	"""
    return pd.read_sql_query(sql_str, connection)["PEOPLE_ORG_CODE_ID"].tolist()


def association_export(year, term, association, connection):
    sql_str = f"""
    SELECT DISTINCT 
        A.PEOPLE_ORG_CODE_ID
        ,P.LAST_NAME
        ,P.FIRST_NAME
        ,A.ASSOCIATION
        ,A.ACADEMIC_YEAR
        ,A.ACADEMIC_TERM
    FROM ASSOCIATION AS A
        INNER JOIN PEOPLE AS P ON A.PEOPLE_ORG_CODE_ID = P.PEOPLE_CODE_ID 
    WHERE ASSOCIATION = '{association}'
        AND A.ACADEMIC_TERM = '{term}' AND A.ACADEMIC_YEAR = '{year}'
    ORDER BY LAST_NAME ASC
        """
    return pd.read_sql_query(sql_str, connection)

