import { Link, useRouteLoaderData } from 'react-router-dom'
import { checkAuthLoader } from '../../utils/auth'
import { BACKEND_URL } from '../../config/envs'
import './CardsList.css'
import PopUpManager from '../../components/PopUpManager'
import { convertToMoneyFormat } from '../../utils/convertToMoneyFormat'
import { CardIcon } from '../../components/CardIcon'

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

const cardType = {
	platinum: 'platinum',
	black: 'black',
	eAid: 'e-dopomoga',
	white: 'white'
}

export const CardsList = () => {
	const cardData = useRouteLoaderData('cards')

	return (
		<div className='cards'>
			<h2 className='cards__title'>Credit Card List</h2>
			<ul className='cards__list'>
				{cardData &&
					cardData.map(({ type, currency, balance, credit_limit }, index) => (
						<li key={index} className='cards__link'>
							<Link className='cards__iconBox' to='#'>
								<CardIcon type={cardType[type]} />
							</Link>
							<div className='cards__infoByCard'>
								<p className='cards__text'>
									<b>Type:</b> <span>{type}</span>
								</p>
								<p className='cards__text'>
									<b>Balance:</b>{' '}
									<span>
										{convertToMoneyFormat(balance)} {currency.symbol}
									</span>
								</p>
								<p className='cards__text'>
									<b>Currency:</b> <span>{currency.name}</span>
								</p>

								<p className='cards__text'>
									<b>Credit Limit:</b>{' '}
									<span>
										{convertToMoneyFormat(credit_limit)} {currency.symbol}
									</span>
								</p>
							</div>
							<Link className='cards__details' to='#'>
								Card Details
							</Link>
						</li>
					))}
			</ul>
		</div>
	)
}
