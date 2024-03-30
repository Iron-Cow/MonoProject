import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom/extend-expect'
import { JarDetails } from '../../pages/JarDetails/JarDetails'
import React from 'react'
import { MemoryRouter, useRouteLoaderData } from 'react-router-dom'
import { convertProgressInPercent } from '../../utils/convertProgressInPercent'

jest.mock('react-router-dom', () => ({
	...jest.requireActual('react-router-dom'),
	useRouteLoaderData: jest.fn()
}))
jest.mock('../../utils/convertProgressInPercent', () => ({
	convertProgressInPercent: jest.fn()
}))

describe('JarDetails component', () => {
	const fakeJarData = {
		id: 1,
		title: 'Test Jar',
		balance: 5000,
		goal: 10000,
		currency: {
			symbol: '$'
		}
	}

	beforeEach(() => {
		useRouteLoaderData.mockReturnValue(fakeJarData)
	})

	test('renders jar details correctly', () => {
		convertProgressInPercent.mockReturnValue('29%')
		render(
			<MemoryRouter>
				<JarDetails />
			</MemoryRouter>
		)

		expect(
			screen.getByText(
				`Balance - ${'50.00' + ' ' + fakeJarData?.currency.symbol}`
			)
		).toBeInTheDocument()
		expect(screen.getByText('Test Jar')).toBeInTheDocument()

		expect(screen.getByTestId('indicate')).toHaveStyle(
			'--dynamic-position: 29%'
		)
		expect(screen.getByTestId('indicate')).toHaveAttribute('data-number', '29%')
		expect(screen.getByText('100.00')).toBeInTheDocument()
		expect(screen.getByText('0.00')).toBeInTheDocument()
	})

	test('render jar without a goal', () => {
		convertProgressInPercent.mockReturnValue('50%')
		const jarWithoutGoal = { ...fakeJarData, goal: null }
		useRouteLoaderData.mockReturnValue(jarWithoutGoal)
		render(<JarDetails />)

		expect(
			screen.getByText(
				`Balance - ${'50.00' + ' ' + fakeJarData?.currency.symbol}`
			)
		).toBeInTheDocument()
		expect(screen.getByText('Test Jar')).toBeInTheDocument()
		expect(screen.queryByText('100.00')).not.toBeInTheDocument()
		expect(screen.queryByText('0.00')).not.toBeInTheDocument()
	})
})
