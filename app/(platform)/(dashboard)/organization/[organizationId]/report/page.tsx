"use client"
import { Separator } from "@/components/ui/separator";

import { Button } from "@/components/ui/button";
import { useState } from "react";
import JSONViewer from "./_components/JSONview";

import ReactMarkdown from 'react-markdown'


const ReportPage =  () => {

  const [dataA, setData] = useState(""); 

  const handleSubmit = (event: { preventDefault: () => void; }) => {
    event.preventDefault(); // Prevent default form submission behavior
    
    fetch('http://localhost:5000/report', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        },
    })
    .then(response => response.json())
    .then(data => {
        console.log('Response:', data.response);
        setData(
          (data.response)); 
        // Handle response data here
    })
    .catch(error => {
        console.error('Error:', error);
        // Handle errors here
    });
};

  return (
    <div className="w-full">
      <Separator className="my-2" />
      <Button variant="primary" onClick={handleSubmit}>Generate Risk and Cost Report</Button>
      <Separator className="my-2" />
      {dataA &&    <div className="px-14 text-justify">
        <ReactMarkdown 
        >{dataA}</ReactMarkdown>
      </div>
      }
      <Separator className="my-2" />

    </div>
  );
};

export default ReportPage;

// <JSONViewer data={dataA} />
/*
mysql:
image: mysql:latest
restart: always
container_name: mysql_db
environment:
  MYSQL_ROOT_PASSWORD: plan-gpt-db
  MYSQL_DATABASE: mydb
  MYSQL_ROOT_USER: root
  MYSQL_PASSWORD: plan-gpt-db
  MYSQL_ROOT_HOST: localhost
ports:
  - 3306:3306
expose:
  - "3306"
volumes:
  - ./data:/var/lib/mysql
*/