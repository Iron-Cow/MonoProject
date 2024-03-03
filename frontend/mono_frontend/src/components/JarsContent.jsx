import { JarIcon } from './JarIcon'
import { ProgressBar } from './ProgressBar'
import { Link } from 'react-router-dom'

export const JarsContent = ({ jar }) => {
	const calcTotalProc = function (balance, goal) {
		return String(Math.round((balance / goal) * 100) + '%')
	}
	return (
		<Link className='jars__link' to='#'>
			<div className='jars__iconBox'>
				<JarIcon />
			</div>

			<h3 className={jar?.goal ? 'marginGoal' : 'marginWithoutGoal'}>
				{jar.title}
			</h3>
			{jar?.goal && (
				<ProgressBar calcFunc={() => calcTotalProc(jar.balance, jar.goal)} />
			)}
			<p className='jars__text'>
				Accumulated {(jar.balance / 100).toFixed(2)} {jar.currency.symbol}
			</p>
		</Link>
	)
}
