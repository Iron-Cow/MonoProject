import './JarDetails.css'
import { Jar } from '../../components/Jar'
import { useRouteLoaderData } from 'react-router-dom'
import { BACKEND_URL } from '../../config/envs'
import { checkAuthLoader } from '../../utils/auth'
import { convertProgressInPercent } from '../../utils/convertProgressInPercent'
import PopUpManager from '../../components/PopUpManager'
import { convertToMoneyFormat } from '../../utils/convertToMoneyFormat'

export const getJarDetails = async function ({ request, params }) {
	const { jarId } = params
	const endpoint = `${BACKEND_URL}/monobank/monojars/${jarId}`
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

export const JarDetails = function () {
	const jar = useRouteLoaderData('jar')
	const progressInPercent = jar?.goal
		? convertProgressInPercent(jar.balance, jar.goal)
		: '50%'
	return (
		<>
			<div className='jar'>
				<div className='jar__box'>
					<h2>
						Balance -{' '}
						{convertToMoneyFormat(jar?.balance) + ' ' + jar?.currency.symbol}
					</h2>
					<div className='jar__iconBox'>
						<Jar percent={progressInPercent} />
						<div className='jar__sticker'>
							<span className='jar__text jar__title'>{jar?.title} </span>
						</div>

						{jar?.goal && (
							<>
								<div className='jar__position'>
									<div className='jar__position-top'>
										{convertToMoneyFormat(jar?.goal)}
									</div>
									<div className='jar__position-bottom'>
										{convertToMoneyFormat(0)}
									</div>
								</div>
								<div
									className='jar__indicate'
									style={{ '--dynamic-position': `${progressInPercent}` }}
									data-number={progressInPercent}
									data-testid='indicate'></div>
							</>
						)}
					</div>
				</div>
			</div>
		</>
	)
}
