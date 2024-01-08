// import './Home.css'
import axios from 'axios'
import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

const INITIAL_STATE = [
  { id: 1, book_Title: 'Tommy', age: 21, hobby: 'coding' },
  { id: 2, name: 'Anna', age: 19, hobby: 'reading' },
  { id: 3, name: 'Bobby', age: 16, hobby: 'swimming' },
  { id: 4, name: 'Lauren', age: 25, hobby: 'running' },
]

const user_name = '1q1'
const token_number = '1q1'
const purchased_books = ['lsdkfaj', 'asfdfd']
const contributed_books = ['sadf ']

const capitalize = (word: string) => {
  return (word[0].toUpperCase() + word.slice(1)).replaceAll('_', ' ')
}

const API_URL = 'http://127.0.0.1:5000/'

export const Home = () => {
  const [users, setUsers] = useState(INITIAL_STATE)

  const loginLink = (
    <Link to="/">
      <button className="logout">Log out</button>
    </Link>
  )

  const handleBuyClick = () => {
    const formData = new FormData()
    formData.append('filename', '123')

    axios
      .post(API_URL + 'download', formData, { headers: formData.getHeaders() })
      .then(async (response) => {
        // if (response.data.accessToken) {
        //   localStorage.setItem('user', JSON.stringify(response.data))
        // }
        console.log(response)
        return response.data
      })
      .catch((error) => {
        console.log(error)
      })
  }

  const handleBookShow = () => {
    return purchased_books.map((book_name) => {
      return <li>{book_name}</li>
    })
  }

  const renderUsers = () => {
    return users.map(({ id, name, age, hobby }) => {
      return (
        <tr key={id}>
          <td>{id}</td>
          <td>{name}</td>
          <td>{age}</td>
          <td>{hobby}</td>
          <td>
            <button onClick={handleBuyClick}>Buy</button>
          </td>
        </tr>
      )
    })
  }

  const renderHeader = () => {
    return (
      <tr>
        {Object.keys(INITIAL_STATE[0]).map((key) => (
          <th>{capitalize(key)}</th>
        ))}
      </tr>
    )
  }

  const renderTable = () => {
    return (
      <table>
        {renderHeader()}
        <tbody>{renderUsers()}</tbody>
      </table>
    )
  }

  return (
    <div className="short:pb-2 short:pt-2 mx-auto flex w-full grow flex-col px-1 pb-8 pt-2 sm:px-6 md:max-w-7xl lg:px-8">
      <h1>Textbook Exchange System</h1>

      {loginLink}

      <div className="book-list">
        <h2>Available Books</h2>
        {renderTable()}
      </div>
      <div className="account-info">
        <h2>Account Information</h2>
        <p>Account ID: {user_name}</p>
        <p>Token Number: </p>
        <p>List of Purchased Books:</p>
        <ul>{handleBookShow()}</ul>
        <p>List of Contributed Books:</p>
        <ul></ul>

        <button className="make_contribute">Make a Contribution</button>
      </div>
    </div>
  )
}

export default Home
