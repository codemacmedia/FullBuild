import React, { useState } from 'react'
import { Button, Form, Col, Row } from 'react-bootstrap'
import { useHistory } from 'react-router-dom'

function SearchBox() {
    const [keyword, setKeyword] = useState('')

    let history = useHistory()

    const submitHandler = (e) => {
        e.preventDefault()
        if (keyword) {
            history.push(`/?keyword=${keyword}&page=1`)
        } else {
            history.push(history.push(history.location.pathname))
        }
    }
    return (
        <div>
            <Row>
                <Col>
                    <Form onSubmit={submitHandler} className="d-flex">
                        <Form.Control
                            type='text'
                            name='q'
                            onChange={(e) => setKeyword(e.target.value)}
                            className="me-2"
                        >
                        </Form.Control>

                        <Button type="submit" variant="outline-success" className="p-2">
                            {'submit'}
                        </Button>
                    </Form>
                </Col>
            </Row>
        </div>
    )
}

export default SearchBox
