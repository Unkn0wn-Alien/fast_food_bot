from typing import Union

import asyncpg
from asyncpg import Connection
from asyncpg.pool import Pool

from config import config


class Database:
    def __init__(self):
        self.pool: Union[Pool, None] = None

    async def create(self):
        self.pool = await asyncpg.create_pool(
            user=config.DB_USER,
            password=config.DB_PASS,
            host=config.DB_HOST,
            database=config.DB_NAME,
        )

    async def execute(
            self,
            command,
            *args,
            fetch: bool = False,
            fetchval: bool = False,
            fetchrow: bool = False,
            execute: bool = False,
    ):
        async with self.pool.acquire() as connection:
            connection: Connection
            async with connection.transaction():
                if fetch:
                    result = await connection.fetch(command, *args)
                elif fetchval:
                    result = await connection.fetchval(command, *args)
                elif fetchrow:
                    result = await connection.fetchrow(command, *args)
                elif execute:
                    result = await connection.execute(command, *args)
            return result

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join(
            [f"{item} = ${num}" for num, item in enumerate(parameters.keys(), start=1)]
        )
        return sql, tuple(parameters.values())

    # async def create_table_users(self):
    #     sql = """
    #     CREATE TABLE IF NOT EXISTS Users (
    #     id SERIAL PRIMARY KEY,
    #     telegram_id BIGINT NOT NULL UNIQUE,
    #     full_name varchar (255) NOT NULL,
    #     language varchar (255) NOT NULL,
    #     phone_number varchar (255) NOT NULL,
    #     created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    #     confirm_code varchar (6) NULL
    #     );
    #     """
    #     await self.execute(sql, execute=True)

    async def add_user(self, telegram_id, full_name, language, phone_number, confirm_code, created_at):
        sql = "INSERT INTO admin_fast_food_users (telegram_id, full_name, language, phone_number, confirm_code, created_at) VALUES ($1, $2, $3, $4, $5,$6) RETURNING *"
        return await self.execute(sql, telegram_id, full_name, language, phone_number, confirm_code, created_at, fetchrow=True)

    async def select_user(self, **kwargs):
        sql = "SELECT * FROM admin_fast_food_users WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def select_user_id(self):
        sql = "SELECT telegram_id FROM admin_fast_food_users"
        return await self.execute(sql, fetch=True)

    async def select_username(self, telegram_id):
        sql = f"SELECT full_name FROM admin_fast_food_users WHERE telegram_id='{telegram_id}'"
        return await self.execute(sql, fetchrow=True)

    async def select_language(self, telegram_id):
        sql = "SELECT language FROM admin_fast_food_users WHERE telegram_id=$1"
        return await self.execute(sql, telegram_id, fetchrow=True)

    async def select_phone_number(self, telegram_id):
        sql = "SELECT phone_number FROM admin_fast_food_users WHERE telegram_id=$1"
        return await self.execute(sql, telegram_id, fetchrow=True)

    async def select_confirm_code(self, telegram_id):
        sql = "SELECT confirm_code FROM admin_fast_food_users WHERE telegram_id=$1"
        return await self.execute(sql, telegram_id, fetchrow=True)

    async def count_users(self):
        sql = "SELECT COUNT(*) FROM admin_fast_food_users"
        return await self.execute(sql, fetchval=True)

    async def update_user_language(self, language_user, telegram_id):
        sql = "UPDATE admin_fast_food_users SET language=$1 WHERE telegram_id=$2"
        return await self.execute(sql, language_user, telegram_id, execute=True)

    async def update_user_phone_number(self, phone_number, telegram_id):
        sql = f"UPDATE admin_fast_food_users SET phone_number={phone_number} WHERE telegram_id={telegram_id}"
        return await self.execute(sql, execute=True)

    async def update_user_fullname(self, full_name, telegram_id):
        sql = "UPDATE admin_fast_food_users SET full_name=$1 WHERE telegram_id=$2"
        return await self.execute(sql, full_name, telegram_id, execute=True)

    async def update_confirm_code(self, confirm_code, phone_number):
        sql = "UPDATE admin_fast_food_users SET confirm_code=$1 WHERE phone_number=$2"
        return await self.execute(sql, confirm_code, phone_number, execute=True)

    # async def create_table_feedbacks(self):
    #     sql = """
    #             CREATE TABLE IF NOT EXISTS Feedbacks (
    #             id SERIAL PRIMARY KEY UNIQUE,
    #             name VARCHAR (255) NOT NULL,
    #             feedback VARCHAR (255) NOT NULL
    #             );
    #             """
    #     await self.execute(sql, execute=True)

    async def add_feedback(self, full_name, feedback, created_at):
        sql = "INSERT INTO admin_fast_food_feedbacks (full_name, feedback, created_at) VALUES ($1, $2, $3) RETURNING *"
        return await self.execute(sql, full_name, feedback, created_at, fetchrow=True)


    # async def create_table_category(self):
    #     sql = """
    #             CREATE TABLE IF NOT EXISTS Category (
    #             id SERIAL PRIMARY KEY UNIQUE,
    #             category_name_uz VARCHAR(255) NOT NULL,
    #             category_name_ru VARCHAR(255) NOT NULL,
    #             category_name_en VARCHAR(255) NOT NULL,
    #             created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    #             updated_at TIMESTAMP NULL DEFAULT NOW(),
    #             deleted_at TIMESTAMP DEFAULT NULL
    #             );
    #             """
    #     await self.execute(sql, execute=True)

    async def get_categories_by_id_uz(self, category_name_uz):
        sql = "SELECT id FROM admin_fast_food_categories WHERE category_name_uz=$1"
        return await self.execute(sql, category_name_uz, fetch=True)

    async def get_categories_by_id_ru(self, category_name_ru):
        sql = "SELECT id FROM admin_fast_food_categories WHERE category_name_ru=$1"
        return await self.execute(sql, category_name_ru, fetch=True)

    async def get_categories_by_id_en(self, category_name_en):
        sql = "SELECT id FROM admin_fast_food_categories WHERE category_name_en=$1"
        return await self.execute(sql, category_name_en, fetch=True)

    async def get_categories_uz(self):
        sql = "SELECT category_name_uz FROM admin_fast_food_categories"
        return await self.execute(sql, fetch=True)

    async def get_categories_ru(self):
        sql = "SELECT category_name_ru FROM admin_fast_food_categories"
        return await self.execute(sql, fetch=True)

    async def get_categories_en(self):
        sql = "SELECT category_name_en FROM admin_fast_food_categories"
        return await self.execute(sql, fetch=True)

    # async def create_table_products(self):
    #     sql = """
    #             CREATE TABLE IF NOT EXISTS Products (
    #             id SERIAL PRIMARY KEY UNIQUE,
    #             product_name_uz VARCHAR(255) NOT NULL,
    #             product_name_ru VARCHAR(255) NOT NULL,
    #             product_name_en VARCHAR(255) NOT NULL,
    #             photo varchar(255) NULL,
    #             price INT NOT NULL,
    #             description_uz varchar (255) NULL,
    #             description_ru varchar (255) NULL,
    #             description_en varchar (255) NULL,
    #             created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    #             updated_at TIMESTAMP NULL DEFAULT NOW(),
    #             deleted_at TIMESTAMP DEFAULT NULL,
    #             category_id INTEGER NOT NULL,
    #             CONSTRAINT fk_category FOREIGN KEY (category_id) REFERENCES category (id)
    #             );
    #             """
    #     await self.execute(sql, execute=True)

    async def get_products(self, category_id):
        sql = f"SELECT * FROM admin_fast_food_products WHERE category_id='{category_id}'"
        return await self.execute(sql, fetch=True)

    async def get_product_by_id_uz(self, product_name_uz):
        sql = "SELECT id FROM admin_fast_food_products WHERE product_name_uz=$1"
        return await self.execute(sql, product_name_uz, fetch=True)

    async def get_product_by_id_ru(self, product_name_ru):
        sql = "SELECT id FROM admin_fast_food_products WHERE product_name_ru=$1"
        return await self.execute(sql, product_name_ru, fetch=True)

    async def get_product_by_id_en(self, product_name_en):
        sql = "SELECT id FROM admin_fast_food_products WHERE product_name_en=$1"
        return await self.execute(sql, product_name_en, fetch=True)

    async def get_product(self, id):
        sql = f"SELECT * FROM admin_fast_food_products WHERE id='{id}'"
        return await self.execute(sql, fetchrow=True)

    # async def create_table_cart(self):
    #     sql = """
    #             CREATE TABLE IF NOT EXISTS Cart (
    #             id SERIAL PRIMARY KEY,
    #             product_name varchar(255) NOT NULL,
    #             price INTEGER NOT NULL,
    #             count INTEGER NOT NULL,
    #             telegram_id BIGINT NOT NULL,
    #             product_id INTEGER NOT NULL
    #             );
    #             """
    #     await self.execute(sql, execute=True)

    async def add_cart(self, product_name, price, count, product_id, telegram_id):
        sql = "INSERT INTO admin_fast_food_cart (product_name, price, count, product_id, telegram_id) VALUES($1, $2, $3, $4, $5) returning *"
        return await self.execute(sql, product_name, price, count, product_id, telegram_id, fetchrow=True)

    async def select_cart(self, telegram_id):
        sql = f"SELECT * FROM admin_fast_food_cart WHERE telegram_id={telegram_id}"
        return await self.execute(sql, fetch=True)

    async def select_cart_if_exist(self, product_id, telegram_id):
        sql = f"SELECT * FROM admin_fast_food_cart WHERE product_id='{product_id}' AND telegram_id='{telegram_id}'"
        return await self.execute(sql, fetch=True)

    async def delete_cart_if_exist(self, product_id, telegram_id):
        sql = f"DELETE FROM admin_fast_food_cart WHERE product_id='{product_id}' AND telegram_id='{telegram_id}'"
        return await self.execute(sql, fetch=True)

    async def get_cart(self):
        sql = "SELECT DISTINCT product_id FROM admin_fast_food_cart"
        return await self.execute(sql, fetch=True)

    async def delete_cart(self, telegram_id):
        sql = f"DELETE FROM admin_fast_food_cart WHERE telegram_id={telegram_id}"
        return await self.execute(sql, execute=True)

    async def update_product_count(self, count, product_id, telegram_id):
        sql = f"UPDATE admin_fast_food_cart SET count={count} WHERE product_id={product_id} AND telegram_id={telegram_id}"
        return await self.execute(sql, execute=True)

    # async def create_table_addresses(self):
    #     sql = """
    #             CREATE TABLE IF NOT EXISTS Address (
    #             id SERIAL PRIMARY KEY UNIQUE,
    #             address VARCHAR(255) NULL,
    #             long VARCHAR(255) NULL,
    #             lat VARCHAR(255) NULL,
    #             telegram_id BIGINT NULL,
    #             created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    #             updated_at TIMESTAMP NULL DEFAULT NOW(),
    #             deleted_at TIMESTAMP DEFAULT NULL
    #             );
    #             """
    #     await self.execute(sql, execute=True)

    async def add_address(self, address, long, lat, telegram_id, created_at):
        sql = "INSERT INTO admin_fast_food_address (address, long, lat, telegram_id, created_at) VALUES($1, $2, $3, $4, $5) returning *"
        return await self.execute(sql, address, long, lat, telegram_id, created_at, fetchrow=True)

    async def select_address(self, telegram_id):
        sql = f"SELECT * FROM admin_fast_food_address WHERE telegram_id={telegram_id}"
        return await self.execute(sql, fetch=True)

    async def delete_address(self, telegram_id):
        sql = f"DELETE FROM admin_fast_food_address WHERE telegram_id={telegram_id}"
        return await self.execute(sql, execute=True)

    # async def create_table_orders(self):
    #     sql = """
    #             CREATE TABLE IF NOT EXISTS Orders (
    #             id SERIAL PRIMARY KEY,
    #             order_code varchar (255) NOT NULL,
    #             telegram_id BIGINT NOT NULL,
    #             created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    #             updated_at TIMESTAMP NULL DEFAULT NOW(),
    #             deleted_at TIMESTAMP DEFAULT NULL
    #             );
    #             """
    #     await self.execute(sql, execute=True)

    async def add_order(self, order_code, telegram_id, created_at):
        sql = "INSERT INTO admin_fast_food_orders (order_code, telegram_id, created_at) VALUES ($1, $2, $3) returning *"
        return await self.execute(sql, order_code, telegram_id, created_at, fetchrow=True)

    async def select_order(self, telegram_id):
        sql = f"SELECT * FROM admin_fast_food_orders WHERE telegram_id={telegram_id}"
        return await self.execute(sql, fetch=True)

    async def select_order_by_id(self, telegram_id):
        sql = f"SELECT id FROM admin_fast_food_orders WHERE telegram_id={telegram_id}"
        return await self.execute(sql, fetch=True)

    # async def create_table_orders_ontime(self):
    #     sql = """
    #             CREATE TABLE IF NOT EXISTS Orders_ontime (
    #             id SERIAL PRIMARY KEY,
    #             order_code varchar (255) NOT NULL,
    #             product_name varchar(255) NOT NULL,
    #             product_id INTEGER NOT NULL,
    #             price INTEGER NOT NULL,
    #             count INTEGER NOT NULL,
    #             telegram_id BIGINT NOT NULL,
    #             phone_number varchar (255) NOT NULL,
    #             created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    #             updated_at TIMESTAMP NULL DEFAULT NOW(),
    #             deleted_at TIMESTAMP DEFAULT NULL
    #             );
    #             """
    #     await self.execute(sql, execute=True)

    async def add_order_ontime(self, order_code, product_name, product_id, price, count, telegram_id, phone_number, created_at):
        sql = "INSERT INTO admin_fast_food_orders_ontime (order_code, product_name, product_id, price, count, telegram_id, phone_number, created_at) VALUES ($1, $2, $3, $4, $5, $6, $7, $8) returning *"
        return await self.execute(sql, order_code, product_name, product_id, price, count, telegram_id, phone_number, created_at, fetchrow=True)

    async def select_order_ontime(self, telegram_id):
        sql = f"SELECT * FROM admin_fast_food_orders_ontime WHERE telegram_id={telegram_id}"
        return await self.execute(sql, fetch=True)

    async def delete_order_ontime(self, telegram_id):
        sql = f"DELETE FROM admin_fast_food_orders_ontime WHERE telegram_id={telegram_id}"
        return await self.execute(sql, execute=True)

    # async def create_table_orders_details(self):
    #     sql = """
    #             CREATE TABLE IF NOT EXISTS Orders_details (
    #             id SERIAL PRIMARY KEY,
    #             order_id INTEGER NOT NULL,
    #             product_id INTEGER NOT NULL,
    #             count INTEGER NOT NULL,
    #             created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    #             updated_at TIMESTAMP NULL DEFAULT NOW(),
    #             deleted_at TIMESTAMP DEFAULT NULL
    #             );
    #             """
    #     await self.execute(sql, execute=True)

    async def add_order_details(self, order_id, product_id, count, created_at):
        sql = "INSERT INTO admin_fast_food_orders_details (order_id, product_id, count, created_at) VALUES ($1, $2, $3, $4) returning *"
        return await self.execute(sql, order_id, product_id, count, created_at, fetchrow=True)

    # async def create_table_orders_for_user(self):
    #     sql = """
    #             CREATE TABLE IF NOT EXISTS Orders_for_user (
    #             id SERIAL PRIMARY KEY,
    #             order_code varchar (255) NOT NULL,
    #             product_name varchar(255) NOT NULL,
    #             price INTEGER NOT NULL,
    #             count INTEGER NOT NULL,
    #             telegram_id BIGINT NOT NULL,
    #             phone_number varchar (255) NOT NULL,
    #             created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    #             updated_at TIMESTAMP NULL DEFAULT NOW(),
    #             deleted_at TIMESTAMP DEFAULT NULL
    #             );
    #             """
    #     await self.execute(sql, execute=True)

    async def add_orders_for_user(self, order_code, product_name, price, count, telegram_id, phone_number, created_at):
        sql = "INSERT INTO admin_fast_food_orders_for_user (order_code, product_name, price, count, telegram_id, phone_number, created_at) VALUES ($1, $2, $3, $4, $5, $6, $7) returning *"
        return await self.execute(sql, order_code, product_name, price, count, telegram_id, phone_number, created_at, fetchrow=True)

    async def select_orders_for_user(self, telegram_id):
        sql = f"SELECT * FROM admin_fast_food_orders_for_user WHERE telegram_id={telegram_id}"
        return await self.execute(sql, fetch=True)