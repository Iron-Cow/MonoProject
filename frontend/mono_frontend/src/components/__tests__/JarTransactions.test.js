import {render, screen} from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import React from 'react';
import {MemoryRouter, useRouteLoaderData} from 'react-router-dom';
import {JarTransactions} from "../JarTransactions";

jest.mock('react-router-dom', () => ({
    ...jest.requireActual('react-router-dom'),
    useRouteLoaderData: jest.fn(),
}));

describe('JarTransactions component', () => {
    const fakeTransactionsData = [
        {
            "id": "bbbbbb",
            "amount": 400000,
            "account_id": "aaaaa",
            "currency": {
                "code": 980,
                "name": "UAH",
                "flag": "🇺🇦",
                "symbol": "₴"
            },
            "balance": 743124,
            "category": "Грошові перекази",
            "category_symbol": "💰",
            "description": "З чорної картки",
            "owner_name": "TestName1"
        },
        {
            "id": "cccccc",
            "amount": -50,
            "account_id": "bbbbbb",
            "currency": {
                "code": 980,
                "name": "UAH",
                "flag": "🇺🇦",
                "symbol": "₴"
            },
            "balance": 743125,
            "category": "Грошові перекази",
            "category_symbol": "💰",
            "description": "18% з нарахованих процентів",
            "owner_name": "TestName1"
        },
    ];

    beforeEach(() => {
        useRouteLoaderData.mockReturnValue(fakeTransactionsData);
    });

    test('renders transactions list correctly', () => {
        render(
            <MemoryRouter>
                <JarTransactions jarTransactions={fakeTransactionsData} isModalOpened={true}/>
            </MemoryRouter>
        );

        expect(
            screen.getByText(
                `Jar Transactions`
            )
        ).toBeInTheDocument()
        let container = screen.getByTestId("transactions-container")
        expect(container.children.length).toBe(2)
        expect(screen.getByText('18% з нарахованих процентів [Залишок 7431.25 ₴]')).toBeInTheDocument()
        expect(screen.getByText('З чорної картки [Залишок 7431.24 ₴]')).toBeInTheDocument()

    });

    test('renders empty message when no transactions are available', () => {
        render(
            <MemoryRouter>
                <JarTransactions jarTransactions={[]} isModalOpened={true}/>
            </MemoryRouter>
        );

        let container = screen.getByTestId("transactions-container")
        expect(container.children.length).toBe(0)
    });
    //
    test('renders error message when data is not available', () => {
        render(
            <MemoryRouter>
                <JarTransactions jarTransactions={null} isModalOpened={true}/>
            </MemoryRouter>
        );

        expect(
            screen.getByText(
                `Jar Transactions`
            )
        ).toBeInTheDocument()
        let container = screen.getByTestId("transactions-container")
        expect(container.children.length).toBe(0)
    });
});
