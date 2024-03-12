import { JarIcon } from './JarIcon'
import { ProgressBar } from './ProgressBar'
import { Link } from 'react-router-dom'
import { convertProgressInPercent } from '../utils/convertProgressInPercent'

export const JarsContent = ({ jar }) => {
	return (
		<Link className='jars__link' to={`/jars/${jar.id}`}>
			<div className='jars__iconBox'>
				<JarIcon />
			</div>

			<h3 className={jar?.goal ? 'marginGoal' : 'marginWithoutGoal'}>
				{jar.title}
			</h3>
			{jar?.goal && (
				<ProgressBar
					calcFunc={() => convertProgressInPercent(jar.balance, jar.goal)}
				/>
			)}
			<p className='jars__text'>
				Accumulated {(jar.balance / 100).toFixed(2)} {jar.currency.symbol}
			</p>
		</Link>
	)
}
