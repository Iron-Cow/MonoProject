import {fireEvent, render, screen} from '@testing-library/react';
import '@testing-library/jest-dom';
import React from 'react';
import {JarDetailsModal} from "../JarDetailsModal";


describe('JarDetailsModal component', () => {
    const fakeJarDetails = {
        id: "jar123",
        send_id: "send123",
        balance: 50000,
        currency: {
            symbol: '₴'
        }
    };


    test('renders jar details correctly when modal is open', () => {
        const setShowModal = jest.fn();

        render(
            <JarDetailsModal jarDetails={fakeJarDetails} isModalOpened={true} setShowModal={setShowModal}/>
        );

        expect(screen.getByText('Jar Details')).toBeInTheDocument();
        expect(screen.getByText('Jar ID:')).toBeInTheDocument();
        expect(screen.getByText('jar123')).toBeInTheDocument();
        expect(screen.getByText('Link to donation')).toHaveAttribute('href', 'https://send.monobank.ua/send123');
        expect(screen.getByText('500.00 ₴')).toBeInTheDocument();
    });

    test('renders nothing when modal is not open', () => {
        const setShowModal = jest.fn();

        const {container} = render(
            <JarDetailsModal jarDetails={fakeJarDetails} isModalOpened={false} setShowModal={setShowModal}/>
        );

        expect(container).toBeEmptyDOMElement();
    });

    test('closes modal on click close button', () => {
        const setShowModal = jest.fn();

        render(
            <JarDetailsModal jarDetails={fakeJarDetails} isModalOpened={true} setShowModal={setShowModal}/>
        );

        fireEvent.click(screen.getByText('×'));
        expect(setShowModal).toHaveBeenCalledWith(false);
    });

    test('renders correctly with undefined or null details', () => {
        const setShowModal = jest.fn();

        render(
            <JarDetailsModal jarDetails={null} isModalOpened={true} setShowModal={setShowModal}/>
        );

        expect(screen.getByText('Jar Details')).toBeInTheDocument();
        expect(screen.queryByText('Jar ID:')).not.toBeInTheDocument();
        expect(screen.queryByText('Link to donation')).not.toBeInTheDocument();
    });
});
