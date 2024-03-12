import { convertToMoneyFormat } from '../convertToMoneyFormat'

describe('convertToMoneyFormat function', () => {
	test('converts integer to money format correctly', () => {
		expect(convertToMoneyFormat(100)).toBe('1.00')
		expect(convertToMoneyFormat(123456)).toBe('1234.56')
	})
	test('returns 0.00 for input of 0', () => {
		expect(convertToMoneyFormat(0)).toBe('0.00')
	})
})
