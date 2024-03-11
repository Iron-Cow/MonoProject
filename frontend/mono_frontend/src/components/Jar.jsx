export const Jar = ({ percent }) => {
	return (
		<>
			<svg
				id='Layer_1'
				data-name='Layer 1'
				xmlns='http://www.w3.org/2000/svg'
				viewBox='0 0 450 700'
				className='jar_icon'
			>
				<defs id='defs1365'>
					<clipPath clipPathUnits='userSpaceOnUse' id='clipPath1383'>
						<rect
							fill='none'
							stroke='#000000'
							paintOrder='markers fill stroke'
							id='rect1385'
							width='352.68469'
							height='535.10785'
							x='44.389626'
							y='131.04062'
						/>
					</clipPath>
				</defs>
				<mask id='maskFirst'>
					<path
						d='m 364.84,173.63 -11.35,-14.57 c -6.28675,-8.13921 -9.94573,-17.99996 -10.49,-28.27 134.28071,-183.544884 -376.560822,-35.921132 -236,0.09 -0.58119,10.22952 -4.25297,20.04186 -10.53,28.14 l -11.31,14.61 c -16.997344,21.91732 -26.243586,48.85417 -26.29,76.59 v 325.87 c -7.866455,109.53784 42.63777,89.65 89.64,89.65 h 153 c 53.92571,0 94.68791,18.4121 89.64,-89.65 V 250.22 c -0.0521,-27.73817 -9.3055,-54.67526 -26.31,-76.59 z'
						id='path1360'
						clipPath='url(#clipPath1383)'
						fill='white'
					/>
				</mask>
				<defs>
					<linearGradient id='gradient-fill' x1='0%' y1='0%' x2='100%' y2='0%'>
						<stop offset='0%' stopColor='#d55222' />
						<stop offset='25%' stopColor='#f79ca1' />
						<stop offset='100%' stopColor='#d55222' />
					</linearGradient>
				</defs>

				<rect
					y='0'
					className='mask'
					width='100%'
					height='100%'
					fill='url(#gradient-fill)'
					mask='url(#maskFirst)'
					opacity='1'
				/>

				<mask id='mask'>
					<path
						d='m 364.84,173.63 -11.35,-14.57 c -6.28675,-8.13921 -9.94573,-17.99996 -10.49,-28.27 134.28071,-183.544884 -376.560822,-35.921132 -236,0.09 -0.58119,10.22952 -4.25297,20.04186 -10.53,28.14 l -11.31,14.61 c -16.997344,21.91732 -26.243586,48.85417 -26.29,76.59 v 325.87 c -7.866455,109.53784 42.63777,89.65 89.64,89.65 h 153 c 53.92571,0 94.68791,18.4121 89.64,-89.65 V 250.22 c -0.0521,-27.73817 -9.3055,-54.67526 -26.31,-76.59 z'
						id='path1360'
						clipPath='url(#clipPath1383)'
						fill='white'
					/>
				</mask>
				<defs>
					<linearGradient id='glassGradient' x1='0%' y1='0%' x2='0%' y2='100%'>
						<stop offset='0%' stopColor='#E6F2FF' />
						<stop offset='10%' stopColor='#D9E5FF' />
						<stop offset='30%' stopColor='#BED3FF' />
						<stop offset='70%' stopColor='#BED3FF' />
						<stop offset='90%' stopColor='#D9E5FF' />
						<stop offset='100%' stopColor='#E6F2FF' />
					</linearGradient>
				</defs>

				<svg viewBox='0 85 450 530'>
					<rect
						y='130px'
						className='mask'
						width='100%'
						height={`calc( 100% - ${percent})`}
						fill='url(#glassGradient)'
						mask='url(#mask)'
					/>
				</svg>

				<defs id='lid'>
					<clipPath clipPathUnits='userSpaceOnUse' id='clipPath820'>
						<ellipse
							fill='none'
							stroke='#000000'
							strokeWidth='1'
							paintOrder='markers fill stroke'
							id='ellipse822'
							cx='225.38829'
							cy='84.886497'
							rx='201.13499'
							ry='56.451618'
						/>
					</clipPath>
				</defs>
				<defs>
					<linearGradient id='gradient-fill2' x1='0%' y1='0%' x2='100%' y2='0%'>
						<stop offset='0%' stopColor='rgb(111 198 241)' />
						<stop offset='100%' stopColor='rgb(13 65 90)' />
					</linearGradient>
				</defs>

				<path
					d='M364.84,173.63l-11.35-14.57A50.63,50.63,0,0,1,343,130.79c14.1-3.59,16.55-7.43,16.55-10.91v-6.13a5.52,5.52,0,0,0-2.77-4.78,5.61,5.61,0,0,0-1.16-.49l-.88-3c3.9-2.26,4.81-4.51,4.81-6.63V92.75a5.55,5.55,0,0,0-1.27-3.51h0a15.44,15.44,0,0,0-5.41-12.46l-.73-.64,1.81-3.28.72-1.31V51.42h-.18c0-4.26-3.09-9.13-40-13.14-23.91-2.59-55.67-4-89.43-4s-65.52,1.43-89.43,4c-35.37,3.84-39.69,8.48-40,12.6h-.2V71l1,1.85,1.51,2.75c-.35.29-.68.59-1,.89A15.38,15.38,0,0,0,91.77,88.7h0a5.52,5.52,0,0,0-1.77,4v6.13c0,2.12.91,4.37,4.81,6.63l-.88,3a5.61,5.61,0,0,0-1.16.49A5.52,5.52,0,0,0,90,113.75v6.13c0,3.52,2.5,7.41,17,11a50.62,50.62,0,0,1-10.53,28.14L85.16,173.63a125.32,125.32,0,0,0-26.29,76.59V576.09a89.64,89.64,0,0,0,89.64,89.65h153a89.64,89.64,0,0,0,89.64-89.65V250.22A125.32,125.32,0,0,0,364.84,173.63Z'
					id='path2'
					fill='url(#gradient-fill2)'
					clipPath='url(#clipPath820)'
				/>
				<path
					fill='none'
					stroke='#3e2c25'
					strokeWidth='1.00146'
					paintOrder='markers fill stroke'
					id='path1145'
					d='M 364.58525,88.989403 A 133.35341,8.4516792 0 0 1 236.12572,97.435389 133.35341,8.4516792 0 0 1 98.23763,89.609314'
					transform='matrix(1,0,-0.07638056,0.99707874,0,0)'
				/>
				<path
					fill='none'
					stroke='#3e2c25'
					paintOrder='markers fill stroke'
					id='path1215'
					d='M 352.09081,75.37336 A 127.01613,8.2586622 0 0 1 227.01862,83.631055 127.01613,8.2586622 0 0 1 98.118051,75.626123'
				/>
				<path
					fill='none'
					stroke='#3e2c25'
					strokeWidth='1'
					paintOrder='markers fill stroke'
					id='path1302'
					d='M 354.75391,105.0023 A 129.70613,11.660822 0 0 1 227.03289,116.66175 129.70613,11.660822 0 0 1 95.402408,105.35919'
				/>
			</svg>
		</>
	)
}
