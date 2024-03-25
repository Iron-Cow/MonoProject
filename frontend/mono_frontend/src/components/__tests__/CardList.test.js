import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom/extend-expect'
import { MemoryRouter, useRouteLoaderData } from 'react-router-dom'
import { CardsList } from '../../pages/CardsList/CardsList'

jest.mock('react-router-dom', () => ({
	...jest.requireActual('react-router-dom'),
	useRouteLoaderData: jest.fn()
}))

describe('CardList render', () => {
	test('renders card data correctly', () => {
		const fakeCardData = [
			{
				id: 'rInaTLo6BrGM-n18NaizuQ',
				send_id: 'SVbbU6VSC',
				currency: {
					code: 980,
					name: 'UAH',
					flag: '🇺🇦',
					symbol: '₴'
				},
				cashback_type: 'UAH',
				balance: 5191,
				credit_limit: 0,
				masked_pan: ['535838******4344', '444111******5203'],
				type: 'platinum',
				iban: 'UA063220010000026204311865605',
				owner_name: 'Фолюшняк Дмитрий'
			},
			{
				id: 'Ud640A_0C9sWhr6dkGisiw',
				send_id: '',
				currency: {
					code: 980,
					name: 'UAH',
					flag: '🇺🇦',
					symbol: '₴'
				},
				cashback_type: 'UAH',
				balance: 0,
				credit_limit: 0,
				masked_pan: ['444111******7363'],
				type: 'eAid',
				iban: 'UA943220010000026207323068680',
				owner_name: 'Фолюшняк Дмитрий'
			}
		]

		useRouteLoaderData.mockReturnValue(fakeCardData)

		render(
			<MemoryRouter>
				<CardsList />
			</MemoryRouter>
		)
		expect(screen.getByText(fakeCardData[0].type)).toBeInTheDocument()
		expect(screen.getByText(fakeCardData[1].type)).toBeInTheDocument()

		const zeroBalanceElements = screen.queryAllByText('0.00 ₴')
		expect(zeroBalanceElements.length).toBe(3)
		const currencyElements = screen.queryAllByText('UAH')
		expect(currencyElements.length).toBe(2)
	})
	test('renders correctly with empty data', () => {
		render(<CardsList />)
		expect(screen.getByText('Credit Card List')).toBeInTheDocument()
	})
})
