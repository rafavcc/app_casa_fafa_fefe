# import_expenses.py
# Script para importar despesas históricas de 2025.
# Execute da raiz do projeto:
#   python -m app.import_expenses

import sys
import re
sys.path.insert(0, ".")

from app.database import get_session, init_db
from app import crud

PAYER_MAP = {
    "Fael": "FAFA",
    "Fe":   "FEFE",
}

RAW_DATA = """EPA	27	1	150.33	Fael	Comida
Ventilador	29	1	80	Fael	Casa
Uber/Taxi/99	5	1	17.52	Fael	Taxi
Uber/Taxi/99	11	1	15.13	Fael	Taxi
Uber/Taxi/99	11	1	9.09	Fael	Taxi
Uber/Taxi/99	18	1	18.31	Fael	Taxi
Uber/Taxi/99	19	1	19.6	Fael	Taxi
Bolao	11	1	86	Fael	Lazer
EPA	18	1	97.34	Fael	Comida
Rosa	10	1	250	Fe	Faxina
Chaves	21	1	50	Fe	Casa
Rosa	27	1	250	Fe	Faxina
Gasolina	2	1	 R$100.00 	Fe	Gasolina
Uber/Taxi/99	4	1	16.66	Fe	Taxi
Gasolina	19	1	 R$100.00 	Fe	Gasolina
EPA	19	1	55.77	Fe	Comida
EPA	21	1	115.6	Fe	Comida
EPA	26	1	81.98	Fe	Comida
Gasolina	29	1	 R$100.00 	Fe	Gasolina
Oficina	6	1	218.41	Fe	Carro
Uber/Taxi/99	11	1	21.99	Fe	Taxi
Seguro	12	1	187.35	Fe	Carro
A Granel	7	2	 R$6.38 	Fael	Comida
EPA	4	2	 R$124.41 	Fael	Comida
EPA	3	2	 R$19.92 	Fael	Comida
EPA	6	2	 R$98.91 	Fael	Comida
Granel	17	2	 R$31.02 	Fael	Comida
Seguro Incedio	20	2	 R$451.23 	Fael	Casa
Amazon	3	2	 R$23.99 	Fael	Casa
EPA	3	2	 R$19.92 	Fael	Comida
EPA	6	2	 R$98.91 	Fael	Comida
Granel	7	2	 R$6.38 	Fael	Comida
Supernosso	11	2	 R$73.49 	Fael	Comida
EPA	14	2	 R$58.86 	Fael	Comida
EPA	14	2	 R$94.48 	Fael	Comida
EPA	15	2	 R$26.00 	Fael	Comida
Barnabe	15	2	 R$92.70 	Fael	Lazer
Pao-de-queijaria	16	2	 R$73.15 	Fael	Lazer
EPA	18	2	 R$45.47 	Fael	Comida
EPA	18	2	 R$11.64 	Fael	Comida
Cervejaria Viela	20	2	 R$65.00 	Fael	Lazer
No Ponto	21	2	 R$92.40 	Fael	Lazer
Bar	22	2	 R$164.07 	Fael	Lazer
Supernosso	24	2	 R$9.98 	Fael	Comida
McDonalds	23	2	 R$53.90 	Fael	Lazer
EPA	25	2	 R$160.88 	Fael	Comida
Feira	26	2	 R$8.00 	Fael	Comida
EPA	26	2	 R$147.94 	Fael	Comida
EPA	26	2	 R$16.74 	Fael	Comida
EPA	28	2	 R$42.07 	Fael	Comida
Comida Carnaval 1o dia	1	3	 R$44.00 	Fael	Lazer
Comida Carnaval 1o dia	1	3	 R$29.00 	Fael	Lazer
EPA	3	3	 R$37.58 	Fael	Comida
Bar do Claudio (Finin+Fefe)	3	3	 R$100.00 	Fael	Lazer
Maue (Fila+Bela)	5	3	 R$168.30 	Fael	Lazer
EPA	8	3	 R$7.98 	Fael	Comida
EPA	11	3	 R$119.30 	Fael	Comida
EPA	11	3	 R$12.00 	Fael	Comida
EPA	12	3	 R$20.38 	Fael	Comida
Amazon	14	3	 R$25.99 	Fael	Casa
Amazon	14	3	 R$17.30 	Fael	Casa
Granel	14	3	 R$34.79 	Fael	Comida
EPA	14	3	 R$148.15 	Fael	Comida
Second House (niver 1 primo Fe)	16	3	 R$170.50 	Fael	Lazer
EPA	19	3	 R$29.25 	Fael	Comida
Verdemar	19	3	 R$191.27 	Fael	Comida
EPA	20	3	 R$106.72 	Fael	Comida
Granel	20	3	 R$16.73 	Fael	Comida
Espasso Gourmet (Date Fe)	21	3	 R$62.99 	Fael	Lazer
Supernosso	24	3	 R$41.61 	Fael	Comida
Granel	27	3	 R$6.51 	Fael	Comida
Almoço	28	3	 R$51.80 	Fael	Comida
EPA	30	3	 R$47.99 	Fael	Comida
Gasolina	30	3	 R$150.00 	Fael	Gasolina
EPA	31	3	 R$22.42 	Fael	Gasolina
EPA	31	3	 R$7.80 	Fael	Gasolina
EPA	1	4	 R$3.98 	Fael	Comida
Pilhas	6	4	 R$67.35 	Fael	Casa
EPA	7	4	 R$39.17 	Fael	Comida
A granel	7	4	 R$2.89 	Fael	Comida
Mercado Livre	9	4	 R$275.88 	Fael	Casa
Amazon	9	4	 R$11.90 	Fael	Casa
EPA	10	4	 R$88.80 	Fael	Gasolina
Gasolina	12	4	 R$50.00 	Fael	Gasolina
EPA	12	4	 R$65.10 	Fael	Casa
Sacolão	16	4	 R$15.00 	Fael	Comida
EPA	16	4	 R$212.94 	Fael	Comida
99 - NIver Natan	18	4	 R$12.40 	Fael	Taxi
EPA	21	4	 R$38.78 	Fael	Comida
EPA	22	4	 R$129.51 	Fael	Comida
99 - Confins	25	4	 R$93.00 	Fael	Taxi
Rosa	28	2	250	Fe	Faxina
Gasolina	7	2	 R$150.00 	Fe	Gasolina
Agua Gas Refil	9	2	 R$159.00 	Fe	Casa
Gasolina	21	2	 R$100.00 	Fe	Gasolina
Allianz	12	2	 R$187.35 	Fe	Carro
Uber bloco	15	2	 R$14.95 	Fe	Taxi
Uber barnabe	15	2	 R$15.75 	Fe	Taxi
Uber casa	15	2	 R$17.95 	Fe	Taxi
Uber	27	2	 R$11.91 	Fe	Taxi
99	2	3	 R$17.93 	Fe	Taxi
99	3	3	 R$26.70 	Fe	Taxi
Gasolina	6	3	 R$100.00 	Fe	Gasolina
Irmaos Becker	21	3	 R$95.56 	Fe	Casa
Gasolina	22	3	 R$100.00 	Fe	Gasolina
EPA	22	3	 R$128.74 	Fe	Comida
Uber	3	3	 R$18.99 	Fe	Taxi
Uber	4	3	 R$20.94 	Fe	Taxi
Uber	5	3	 R$21.27 	Fe	Taxi
Allianz	12	3	 R$187.35 	Fe	Carro
Uber	1	3	 R$13.93 	Fe	Taxi
EPA	6	4	 R$231.78 	Fe	Comida
EPA	19	4	111.2	Fe	Comida
99	19	4	 R$23.80 	Fe	Taxi
Gasolina	20	4	 R$150.00 	Fe	Gasolina
99	25	4	 R$78.40 	Fe	Taxi
99	25	4	 R$20.32 	Fe	Taxi
99	26	4	 R$16.20 	Fe	Taxi
99	26	4	 R$23.20 	Fe	Taxi
Solar Engenho	25	4	 R$219.98 	Fe	Lazer
Allianz	12	4	 R$187.35 	Fe	Carro
Ifood	24	4	 R$82.70 	Fe	Lazer
EPA	23	4	 R$45.48 	Fe	Comida
Pais De Pet	22	5	294.9	Fael	Bacana
Pais De Pet	10	5	289.9	Fael	Bacana
Rosa	22	5	250	Fael	Casa
Dma Distribuidora Sa	22	5	191.09	Fael	Comida
Alipay	15	5	157.67	Fael	Bacana
Mercado Livre	21	5	103.92	Fael	Bacana
Posto Chicago	21	5	100	Fael	Carro
Supermercado Epa	7	5	96.02	Fael	Comida
Pet Happy	14	5	94.9	Fael	Bacana
Dma Distribuidora Sa	15	5	88.15	Fael	Comida
99	28	5	71.5	Fael	Taxi
Amazon	8	5	59.23	Fael	Casa
Hiper Sacolao Hortisul	22	5	49.99	Fael	Comida
Hiper Sacolao Hortisul	22	5	49.99	Fael	Comida
99	28	5	49.7	Fael	Taxi
Dma Distribuidora Sa	11	5	37.38	Fael	Comida
Dma Distribuidora Sa	19	5	36.58	Fael	Comida
Dma Distribuidora Sa	22	5	28.05	Fael	Comida
Supermercado Epa	14	5	27.8	Fael	Comida
99	27	5	24.6	Fael	Taxi
Amazon	21	5	22.66	Fael	Casa
Dma Distribuidora Sa	20	5	20.64	Fael	Comida
99	27	5	20.1	Fael	Taxi
Shopee(Mandolin)	22	5	19	Fael	Casa
Uber	28	5	17.79	Fael	Taxi
Amazon	8	5	15.9	Fael	Casa
Concessionaria Da Rodo	3	5	15.5	Fael	Lazer
Uber	27	5	13.26	Fael	Taxi
Dma Distribuidora Sa	11	5	12.57	Fael	Comida
99	28	5	7.46	Fael	Taxi
Dma Distribuidora Sa	11	5	6.48	Fael	Comida
Sacolao - Frango	1	6	49.99	Fael	Comida
Amazon	4	6	27.78	Fael	Casa
Forninho	6	6	130	Fael	Casa
Pais De Pet	6	6	143.3	Fael	Bacana
Meli	8	6	430.55	Fael	Casa
Bacana - Petz	10	6	72	Fael	Bacana
Casa Reparo	14	6	10	Fael	Casa
Casa Reparo	14	6	16.3	Fael	Casa
Frango Domingo	15	6	60	Fael	Comida
EPA	15	6	26.16	Fael	Comida
EPA	15	6	26.05	Fael	Comida
EPA	19	6	99.08	Fael	Comida
Kalunga	20	6	6.9	Fael	Casa
Kalunga	20	6	40.2	Fael	Casa
Meli	20	6	38.99	Fael	Casa
Meli	20	6	21.99	Fael	Casa
Petz	23	6	50.98	Fael	Casa
Café Parada Estrada	29	6	127	Fael	Comida
Rosa	6	6	250	Fael	Faxina
Gasolina	3	5	153.31	Fe	Gasolina
Petz	10	5	110.66	Fe	Bacana
Epa	18	5	151.15	Fe	Comida
Cobasi	24	5	113.87	Fe	Bacana
Epa	30	5	133.82	Fe	Comida
Gasolina	31	5	150	Fe	Gasolina
Seguro Carro	12	5	187.35	Fe	Carro
Rosa	31	5	250	Fe	Faxina
Epa	20	6	43.58	Fe	Comida
Petz	10	6	243.67	Fe	Bacana
Petz	17	6	76	Fe	Bacana
Gasolina	18	6	150	Fe	Gasolina
Seguro Carro	12	6	187.5	Fe	Carro
Banho Bacana	1	6	40	Fe	Bacana
Banho Bacana	1	7	70	Fe	Bacana
Rosa	30	6	250	Fe	Faxina
Uber Leitin	27	7	20.23	Fe	Taxi
Uber Cona	27	7	9.47	Fe	Taxi
Vacinas	25	7	252	Fe	Bacana
Daki	22	7	152.28	Fe	Comida
99 Curitiba	19	7	52.8	Fe	Taxi
Petz	28	7	104.47	Fe	Bacana
Cobasi	1	7	30	Fe	Bacana
Sapato Heloisa	2	7	175.81	Fe	Bacana
Adestrador Bacana	3	7	175	Fe	Bacana
Leitin -- Gil	26	7	20.3	Fael	Taxi
99 Curitiba	20	7	15.39	Fael	Taxi
99 Curitiba	20	7	25.29	Fael	Taxi
Cerveja Festa Gil	27	7	50.6	Fael	Lazer
Estacionamento Confins	18	7	53.2	Fael	Lazer
Almoço Sabado Curitiba	28	7	54	Fael	Lazer
Gasolina	13	7	150	Fael	Gasolina
Rosa	2	7	250	Fael	Faxina
Epa	26	7	47.82	Fael	Comida
Amazon - Pe Porta	11	7	12.52	Fael	Casa
Amazon Luva Pequena	23	7	8	Fael	Casa
Amazon Luva Pequena	23	7	12.67	Fael	Casa
Amazon Pulverizador	19	7	16.1	Fael	Casa
Petz	13	7	22.99	Fael	Bacana
Pais de Pet	3	7	122	Fael	Bacana
Taxi	20	8	10.1	Fael	Taxi
Aliexpress	4	9	70.49	Fael	Casa
Amazonmktplc Mouracome	23	9	24.9	Fael	Casa
Mercado Livre	30	8	70.43	Fael	Casa
Fatura inter	25	8	690.94	Fael	Cartao
Fatura Inter	30	9	1443.79	Fael	Cartao
Rosa	20	10	250	Fael	Faxina
Rosa	26	9	250	Fael	Faxina
Rosa	10	9	250	Fael	Faxina
99	4	9	10.3	Fael	Taxi
Rosa	13	8	250	Fael	Faxina
Rosa	30	10	250	Fael	Faxina
Fatura Inter	31	10	1926.15	Fael	Cartao
Rosa	4	8	250	Fe	Faxina
Sacolão	11	8	49.99	Fe	Comida
Rosa	27	8	250	Fe	Faxina
Petz	1	8	59.43	Fe	Bacana
Gasolina	3	8	147.5	Fe	Gasolina
Rodo	7	8	63.86	Fe	Casa
Epa	10	8	88	Fe	Comida
99	14	8	26.5	Fe	Taxi
Amazon	25	8	17.98	Fe	Casa
99	30	8	39.49	Fe	Taxi
Uber	15	8	12.52	Fe	Taxi
Uber	30	8	17.01	Fe	Taxi
Lavagem Carro	17	9	60	Fe	Carro
Presente Elisa	5	9	134.8	Fe	Lazer
99	6	9	18.6	Fe	Taxi
99	6	9	23.4	Fe	Taxi
Gasolina	7	9	150	Fe	Gasolina
Epa	17	9	49	Fe	Casa
Mercado Novo	26	9	36	Fe	Lazer
Allianz	11	9	180.26	Fe	Carro
Allianz	14	10	181.21	Fe	Carro
Vivara	1	10	120	Fe	Casa
Petz	8	10	58.46	Fe	Bacana
Supernosso	10	10	102.04	Fe	Comida
Papabelinha	25	10	77	Fe	Casa
Amazon	25	10	77.26	Fe	Casa
Amazon	13	10	37.53	Fe	Casa
Nutag	30	11	14.73	Fael	Lazer
Nutag	30	11	14.73	Fael	Lazer
Nutag	10	12	18	Fael	Lazer
Amazon Marketplace	22	11	120.95	Fael	Casa
Pet Happy Unidade Sio	26	12	120	Fael	Bacana
Drogaria Araujo	28	11	99.9	Fael	Casa
Amazon	27	11	54.88	Fael	Casa
Amazonmktplc Cauefabre	27	11	42.65	Fael	Casa
Amazonmktplc Novasdnco	22	11	29.48	Fael	Casa
Amazon	30	11	25.19	Fael	Casa
Amazon	22	11	22.66	Fael	Casa
Uber	14	12	20.98	Fael	Taxi
Amazon Marketplace	22	11	18.52	Fael	Casa
Uber	1	12	12.51	Fael	Taxi
Pet Happy Unidade Sio	26	12	9.9	Fael	Bacana
Uber	1	12	3	Fael	Taxi
Growth Supplements	1	11	468.87	Fael	Comida
Guilherme De Castro Martino	17	11	330	Fael	Lazer
Rosa	4	12	280	Fael	Faxina
Rosa	17	12	250	Fael	Faxina
Pix Marketplace	28	11	247.84	Fael	Lazer
Cesar Francisco Martins	15	12	80	Fael	Lazer
Nubank	22	12	47.46	Fael	Carro
Nayara Marques De Paula	14	12	36	Fael	Lazer
Nubank	30	12	29.46	Fael	Carro
Fatura Inter	30	11	1775.82	Fael	Cartao
Fatura Inter	31	12	1024.61	Fael	Cartao"""


def clean_value(raw: str) -> float:
    """Remove R$, espaços e converte para float."""
    cleaned = re.sub(r"[R$\s]", "", raw)
    cleaned = cleaned.replace(",", ".")
    return float(cleaned)


def parse_rows(raw: str):
    rows = []
    skipped = []

    for line_num, line in enumerate(raw.splitlines(), start=1):
        line = line.strip()
        if not line:
            continue

        parts = line.split("\t")
        if len(parts) < 6:
            skipped.append(f"Linha {line_num}: colunas insuficientes — '{line}'")
            continue

        place     = parts[0].strip()
        day_raw   = parts[1].strip()
        month_raw = parts[2].strip()
        value_raw = parts[3].strip()
        payer_raw = parts[4].strip()
        cat_raw   = parts[5].strip()

        if not place:
            skipped.append(f"Linha {line_num}: local vazio")
            continue

        paid_by = PAYER_MAP.get(payer_raw)
        if not paid_by:
            skipped.append(f"Linha {line_num}: pagante desconhecido '{payer_raw}' — '{place}'")
            continue

        try:
            value = clean_value(value_raw)
            if value <= 0:
                raise ValueError("valor zero ou negativo")
        except Exception:
            skipped.append(f"Linha {line_num}: valor inválido '{value_raw}' — '{place}'")
            continue

        try:
            day   = int(day_raw)
            month = int(month_raw)
        except ValueError:
            skipped.append(f"Linha {line_num}: dia/mês inválido — '{place}'")
            continue

        rows.append({
            "place":         place,
            "day":           day,
            "month":         month,
            "year":          2025,
            "value":         value,
            "paid_by":       paid_by,
            "category_name": cat_raw,
            "notes":         None,
        })

    return rows, skipped


def import_expenses():
    init_db()
    rows, skipped = parse_rows(RAW_DATA)

    print(f"\n📋 {len(rows)} linhas válidas encontradas")
    if skipped:
        print(f"⚠️  {len(skipped)} linhas puladas:")
        for s in skipped:
            print(f"   • {s}")

    print("\nInserindo no banco...")
    with get_session() as db:
        for row in rows:
            crud.create_variable_expense(db, row)

    print(f"✅ {len(rows)} despesas inseridas com sucesso!")


if __name__ == "__main__":
    import_expenses()