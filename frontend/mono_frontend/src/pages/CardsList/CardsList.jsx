import { useEffect, useState } from 'react'
import { BACKEND_URL } from '../../config/envs'
import './CardsList.css'

export const getCards = async function (token) {
	const endpoint = `${BACKEND_URL}/monobank/monocards`

	const response = await fetch(endpoint, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		}
	})
	const data = await response.json()

	if (!response.ok) {
		return null
	}
	return data
}

export const CardsList = ({ getToken }) => {
	const [cardData, setCardData] = useState(null)
	const [token, setToken] = useState(null)

	useEffect(() => {
		async function fetchData(token) {
			try {
				const response = await token
				setToken(response)
			} catch (error) {
				console.error(error)
			}
		}

		let ignore = fetchData(getToken)
	})

	useEffect(() => {
		const fetchData = async function () {
			try {
				const access = await getCards(token)
				setCardData(access)
			} catch (error) {
				console.error('Error fetching card data:', error)
			}
		}

		let ignore = fetchData()
	}, [token])

	return (
		<>
			{cardData && (
				<div>
					<table className='table'>
						<thead className='table__head'>
							<tr key={1} className='table__row'>
								<th className='table__title'>№</th>
								<th className='table__title'>Type</th>
								<th className='table__title'>Balance</th>
								<th className='table__title'>Currency</th>
								<th className='table__title'>Credit limit</th>
							</tr>
						</thead>
						<tbody className='table__body'>
							{cardData.map(
								({ id, type, currency, balance, credit_limit }, index) => (
									<tr className='table__body_tr' key={index}>
										<td className='table__description'>{index + 1}</td>
										<td className='table__description'>{type}</td>
										<td className='table__description'>
											{(balance / 100).toFixed(2)}
										</td>
										<td className='table__description'>{currency.name}</td>
										<td className='table__description'>
											{credit_limit.toFixed(2)}
										</td>
									</tr>
								)
							)}
						</tbody>
					</table>
				</div>
			)}
		</>
	)
}
