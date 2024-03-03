export const ProgressBar = ({ calcFunc }) => {
	const progress = calcFunc()
	return (
		<>
			<div className='progress-bar'>
				<span
					style={{
						width: `${progress}`
					}}
				>
					{progress}
				</span>
			</div>
			<div
				className='jars_progressLine'
				style={{
					'--dynamic-width': `${progress}`
				}}
			></div>
		</>
	)
}
