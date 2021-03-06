# queries to extract bank and customer-related information
import pandas as pd

from mies.schema.bank import (
    Account,
    Insurer,
    Person
)

from mies.utilities.connections import connect_bank


def query_accounts_by_person_id(person_ids, bank_name, account_type):
    """
    get all the accounts for each person id in a list of person ids
    """
    session, connection = connect_bank(bank_name)

    accounts_query = session.query(
        Person.person_id,
        Person.customer_id,
        Account.account_id
    ).outerjoin(
        Account,
        Person.customer_id == Account.customer_id
    ).filter(
        Account.account_type == account_type
    ).statement

    accounts = pd.read_sql(
        accounts_query,
        connection
    )

    accounts = accounts[accounts['person_id'].isin(person_ids)]

    connection.close()

    return accounts


def query_accounts_by_company_id(insurer_ids, bank_name, account_type):
    """
    get all bank accounts for each insurer in a list of insurer ids
    """
    session, connection = connect_bank(bank_name)

    accounts_query = session.query(
        Insurer.insurer_id,
        Insurer.customer_id,
        Account.account_id
    ).outerjoin(
        Account,
        Insurer.customer_id == Account.customer_id
    ).filter(
        Account.account_type == account_type
    ).statement

    accounts = pd.read_sql(
        accounts_query,
        connection
    )

    accounts = accounts[accounts['insurer_id'].isin(insurer_ids)]

    connection.close()

    return accounts


def query_customers_by_insurer_id(insurer_ids, bank_name):
    """
    get corresponding customer ids for each insurer id in a list of insurer ids
    """

    session, connection = connect_bank(bank_name)

    customer_query = session.query(Insurer).statement

    customers = pd.read_sql(customer_query, connection)

    customers = customers[customers['insurer_id'].isin(insurer_ids)]

    customers = customers['customer_id']

    connection.close()

    return customers


def query_customers_by_person_id(person_ids, bank_name):
    """
    get corresponding customer ids for each person id in a list of person ids
    """
    session, connection = connect_bank(bank_name)

    customer_query = session.query(Person).statement

    customers = pd.read_sql(customer_query, connection)

    customers = customers[customers['person_id'].isin(person_ids)]

    customers = customers['customer_id']

    connection.close()

    return customers
