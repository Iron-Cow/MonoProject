import { render, screen, waitFor } from '@testing-library/react'
import '@testing-library/jest-dom/extend-expect'
import { JarDetails } from '../../pages/JarDetails/JarDetails'
import React from 'react'
import userEvent from '@testing-library/user-event'
import { useRouteLoaderData } from 'react-router-dom'
import { checkAuthLoader } from '../../utils/auth'
import { convertProgressInPercent } from '../../utils/convertProgressInPercent'

jest.mock('react-router-dom', () => ({
	...jest.requireActual('react-router-dom'),
	useRouteLoaderData: jest.fn()
}))
jest.mock('../../utils/convertProgressInPercent', () => ({
	convertProgressInPercent: jest.fn()
}))

describe('JarDetails component', () => {
	const jarData = {
		id: 1,
		title: 'Test Jar',
		balance: 5000,
		goal: 10000,
		currency: {
			symbol: '$'
		}
	}

	beforeEach(() => {
		useRouteLoaderData.mockReturnValue(jarData)
	})

	test('renders jar details correctly', () => {
		convertProgressInPercent.mockReturnValue('29%')
		render(<JarDetails />)

		const correctBalance = (jarData?.balance / 100).toFixed(2)

		expect(
			screen.getByText(content => content.includes(`${correctBalance}`))
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
		const jarWithoutGoal = { ...jarData, goal: null }
		const correctBalance = (jarData?.balance / 100).toFixed(2)
		useRouteLoaderData.mockReturnValue(jarWithoutGoal)
		render(<JarDetails />)
		expect(
			screen.getByText(content => content.includes(`${correctBalance}`))
		).toBeInTheDocument()

		expect(screen.getByText('Test Jar')).toBeInTheDocument()
		expect(screen.getByTestId('indicate')).toHaveStyle(
			'--dynamic-position: 50%'
		)
		expect(screen.queryByText('100.00')).not.toBeInTheDocument()
		expect(screen.queryByText('0.00')).not.toBeInTheDocument()
	})
})
