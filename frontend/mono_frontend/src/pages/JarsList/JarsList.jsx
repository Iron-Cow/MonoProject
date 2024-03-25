import { useRouteLoaderData } from 'react-router-dom'
import './JarsList.css'
import { BACKEND_URL } from '../../config/envs'
import PopUpManager from '../../components/PopUpManager'
import { checkAuthLoader } from '../../utils/auth'
import { convertToMoneyFormat } from '../../utils/convertToMoneyFormat'
import { JarsContent } from '../../components/JarsContent'

export const getJars = async function () {
	const endpoint = `${BACKEND_URL}/monobank/monojars`
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

export const JarsList = function () {
	const jars = useRouteLoaderData('jars')

	const totalSum = jars ? jars.reduce((sum, jar) => sum + jar.balance, 0) : null

	return (
		<div className='jars'>
			<div className='jars__box'>
				<h1 className='jars__title'>Jars</h1>
				<p className='jars__textMoney'>
					Total balance in all your JARS: {convertToMoneyFormat(totalSum)} ₴
				</p>
				<ul className='jars__list'>
					{jars &&
						jars.map((jar, index) => (
							<li key={index} className='jars__item'>
								<JarsContent jar={jar} />
							</li>
						))}
				</ul>
			</div>
		</div>
	)
}
