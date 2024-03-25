import { useRouteLoaderData } from 'react-router-dom'
import { checkAuthLoader } from '../../utils/auth'
import { BACKEND_URL } from '../../config/envs'
import './CardsList.css'
import PopUpManager from '../../components/PopUpManager'
import {convertToMoneyFormat} from "../../utils/convertToMoneyFormat";

export const getCards = async function () {
	const endpoint = `${BACKEND_URL}/monobank/monocards`
	const token = await checkAuthLoader()
	try {
		const response = await fetch(endpoint, {
			method: 'GET',
			headers: {
				'Content-Type': 'application/json',
				Authorization: `Bearer ${token}`
			}
		})
		return await response.json()
	} catch (error) {
		setTimeout(() => {
			PopUpManager.addPopUp(
				`Error fetching jars data: ${error.message}`,
				'error'
			)
		}, 100)

		return null
	}
}

export const CardsList = () => {
	const cardData = useRouteLoaderData('cards')

	return (
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
				{cardData && cardData.map(
					({ id, type, currency, balance, credit_limit }, index) => (
						<tr className='table__body_tr' key={index}>
							<td className='table__description'>{index + 1}</td>
							<td className='table__description'>{type}</td>
							<td className='table__description'>
								{convertToMoneyFormat(balance)}
							</td>
							<td className='table__description'>{currency.name}</td>
							<td className='table__description'>
								{convertToMoneyFormat(credit_limit)}
							</td>
						</tr>
					)
				)}
				</tbody>
			</table>
		</div>
	)
}
