import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom/extend-expect'
import { JarsList } from '../../pages/JarsList/JarsList'
import { MemoryRouter, useRouteLoaderData } from 'react-router-dom'

jest.mock('react-router-dom', () => ({
	...jest.requireActual('react-router-dom'),
	useRouteLoaderData: jest.fn()
}))
describe('JarsList with jars data', () => {
	test('renders correctly with jars data', () => {
		const fakeJarsData = [
			{
				id: 'akN3vV3YdQ83AO2VdQAomCAGLa7Hn_M',
				send_id: 'jar/A2DWcQG7t2',
				title: 'На День Народження',
				currency: {
					code: 980,
					name: 'UAH',
					flag: '🇺🇦',
					symbol: '₴'
				},
				balance: 500,
				goal: null,
				owner_name: 'Фолюшняк Дмитрий'
			},
			{
				id: 'VBfbylINmyyGz0q0HcUnBBRA_QyvzIs',
				send_id: 'jar/hvCGWwEHw',
				title: 'на мрію',
				currency: {
					code: 980,
					name: 'UAH',
					flag: '🇺🇦',
					symbol: '₴'
				},
				balance: 2000,
				goal: 20000,
				owner_name: 'Фолюшняк Дмитрий'
			}
		]
		useRouteLoaderData.mockReturnValue(fakeJarsData)

		render(
			<MemoryRouter>
				<JarsList />
			</MemoryRouter>
		)

		expect(
			screen.getByText('Total balance in all your JARS: 25.00 ₴')
		).toBeInTheDocument()
		expect(screen.getByText('На День Народження')).toBeInTheDocument()
		expect(screen.getByText('на мрію')).toBeInTheDocument()
		expect(screen.getByText('Accumulated 20.00 ₴')).toBeInTheDocument()
		expect(screen.getByText('Accumulated 5.00 ₴')).toBeInTheDocument()
		expect(screen.queryByText('10%')).toBeInTheDocument()
	})

	test('renders correctly with empty data', () => {
		render(<JarsList />)

		expect(
			screen.getByText('Total balance in all your JARS: 0.00 ₴')
		).toBeInTheDocument()
	})
})
