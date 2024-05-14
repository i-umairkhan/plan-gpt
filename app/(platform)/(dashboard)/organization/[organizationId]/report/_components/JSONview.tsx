"use Client"
import React from 'react';

function JSONViewer({ data }: { data: any }) {
  const renderValue = (value: unknown) => {
    if (typeof value === 'object') {
      return <JSONViewer data={value} />;
    } else {
      return <span>{JSON.stringify(value)}</span>;
    }
  };

  return (
    <div>
      {Object.entries(data).map(([key, value]) => (
        <div key={key}>
          <strong>{key}:</strong> {renderValue(value)}
        </div>
      ))}
    </div>
  );
}

export default JSONViewer;

/*      Now return the response in the form of JSON object.
Do not include Response: ```json``` in the response.
Also remove ``` from start and end of response.
Also remove Response key word from start of response.   
Give valid json Object so that it can be Parsed by front end function JSON.parse(response)
Do not include any "\n" qoutes or special chrectars just give the response in JSON format. 
Do not include any non-whitespace characters before or after the JSON object.
Result should include json and only no other text or code should be included in the response. The JSON should be in this format:
*/