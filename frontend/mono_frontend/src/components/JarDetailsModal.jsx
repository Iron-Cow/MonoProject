import React from 'react';
import {convertToMoneyFormat} from "../utils/convertToMoneyFormat";

export function JarDetailsModal({jarDetails, isModalOpened, setShowModal}) {
    const closeModal = () => {
        setShowModal(false);
    };

    return (
        <>

            {isModalOpened && (
                <>
                    <div className="modal">
                        <div className="modal-content">
                            <span className="close" onClick={closeModal}>×</span>
                            <h2>Jar Details</h2>
                            {jarDetails != null && <div>
                                <p>
                                    <span>Jar ID: </span> <span>{jarDetails.id}</span>
                                </p>
                                <p>
                                    <span>Link to donation: {jarDetails.send_id} </span>
                                    <a href={`https://send.monobank.ua/${jarDetails.send_id}`} target="_blank">Link to
                                        donation</a>
                                </p>
                                <p>
                                    <span>Balance: </span>
                                    <span>{jarDetails?.balance && convertToMoneyFormat(jarDetails?.balance) + ' ' + jarDetails?.currency?.symbol}</span>
                                </p>
                            </div>}
                        </div>

                    </div>
                </>

            )}
        </>
    );
}
