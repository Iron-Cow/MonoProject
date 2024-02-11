import { render, screen } from '@testing-library/react'
import { CardsList } from './CardsList'
import '@testing-library/jest-dom/extend-expect'

jest.useRealTimers()

test('renders card data correctly', async () => {
	const mockTokenFunc = jest.fn().mockResolvedValue('mockToken')

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

	global.fetch = jest.fn().mockResolvedValue({
		ok: true,
		json: () => Promise.resolve(fakeCardData)
	})

	render(<CardsList func={mockTokenFunc} />)

	await screen.findByText('Type')

	expect(screen.getByText(fakeCardData[0].type)).toBeInTheDocument()
	expect(screen.getByText(fakeCardData[1].type)).toBeInTheDocument()
	expect(
		screen.getByText((fakeCardData[0].balance / 100).toFixed(2))
	).toBeInTheDocument()

	const zeroBalanceElements = screen.queryAllByText('0.00')
	expect(zeroBalanceElements.length).toBe(3)
	const currencyElements = screen.queryAllByText('UAH')
	expect(currencyElements.length).toBe(2)
})
