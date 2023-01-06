from pyspark.sql import DataFrame
from pyspark.sql.functions import col


def cast_datatype(df: DataFrame, cast_mapper: dict) -> DataFrame:
    """cast_datatype casts the data type of column in dataframe to a desired type as defined in
        cast_mapper

    Parameters
    ----------
    df : DataFrame
        Spark DataFrame for which columns need to be renamed
    mapper : dict
        dictionary with
            {"columname": "desired_DATATYPE"}

    Returns
    -------
    DataFrame
        Output DataFrame with datatype hanges.
    """
    columns_list = []
    for column_name in df.columns:
        if column_name in cast_mapper.keys():
            columns_list.append(col(column_name).cast(cast_mapper[column_name]))
        else:
            columns_list.append(column_name)

    return df.select(columns_list)


def join_dataframes(
    df1: DataFrame,
    df2: DataFrame,
    join_columns: list,
    join_how: str,
) -> DataFrame:
    """This function joins 2 Spark Dataframes on provided columns and the join type.

    Parameters
    ----------
    df1 : DataFrame
        Base DataFrame to which to join
    df2 : DataFrame
        Right side of the join
    join_columns : list
        Columns index list on which to join the dataframes.
    join_how : str
        type of join to use for joining df1 & df2.
        "inner", "left", "right", inner, cross, full, semi, anti etc.

    Returns
    -------
    DataFrame
        Joined Spark DataFrame.
    """

    return df1.join(other=df2, on=join_columns, how=join_how)
