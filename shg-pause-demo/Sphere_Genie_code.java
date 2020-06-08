private static final
String CAT_URL = "http://192.168.1.99";

//private static final String PAUSE_URL = "http://192.168.0.10:8080/pause";

private static final
String BATTERY_STATUS_URL = CAT_URL + "/query_battery.php";

private static final
String SYSTEM_STATUS_URL = CAT_URL + "/query_status.php";

private static final
String START_RECORDING_URL = CAT_URL + ":8161/api/message/SPHERE.CTRL.SHG?type=topic";

private static final
String DELETE_URL_TESTING = CAT_URL + ":8161/api/message?destination=topic://SPHERE.CTRL.SHG.CONF&oneShot=true";

private static final
int REQUEST_SYSTEM_STATUS_FREQUENCY = 7000;







package sphere.dashbord;




import android.content.Context;

import android.content.Intent;

import android.net.ConnectivityManager;

import android.net.NetworkInfo;

import android.os.Handler;

import android.support.v7.app.AppCompatActivity;

import android.os.Bundle;

import android.util.Base64;

import android.util.Log;

import android.view.Gravity;

import android.view.View;

import android.widget.Button;

import android.widget.TextView;

import android.widget.Toast;




import com.android.volley.Request;

import com.android.volley.Response;

import com.android.volley.VolleyError;

import com.android.volley.VolleyLog;

import com.android.volley.toolbox.JsonObjectRequest;

import com.android.volley.toolbox.StringRequest;




import org.json.JSONException;

import org.json.JSONObject;




import java.text.DateFormat;

import java.text.ParseException;

import java.text.SimpleDateFormat;

import java.util.Date;

import java.util.HashMap;

import java.util.LinkedHashMap;

import java.util.Locale;

import java.util.Map;

import java.util.TimeZone;

import java.util.Timer;

import java.util.TimerTask;




import static sphere.dashbord.R.id.battery3;

import static sphere.dashbord.R.id.battery4;

import static sphere.dashbord.R.id.label3;

import static sphere.dashbord.R.id.label4;




public class HomeActivity
extends AppCompatActivity {




static TextView status_top;

static TextView status_bottom;

Button pauseButton;

Button deleteButton;

Button contactButton;

Button chartsButton;




private static final
String CAT_URL = "http://192.168.1.99";

//private static final String PAUSE_URL = "http://192.168.0.10:8080/pause";

private static final
String BATTERY_STATUS_URL = CAT_URL + "/query_battery.php";

private static final
String SYSTEM_STATUS_URL = CAT_URL + "/query_status.php";

private static final
String START_RECORDING_URL = CAT_URL + ":8161/api/message/SPHERE.CTRL.SHG?type=topic";

private static final
String DELETE_URL_TESTING = CAT_URL + ":8161/api/message?destination=topic://SPHERE.CTRL.SHG.CONF&oneShot=true";

private static final
int REQUEST_SYSTEM_STATUS_FREQUENCY = 7000;




boolean systemStatusCheckerRunning = false;




boolean isLayoutReady = false;

boolean isFirstRun = true;

Map <String, String>
batteryInfo = new HashMap<>();

Map <String, BatteryInfo>
batteryObjects = new LinkedHashMap<>();




@Override

protected void onCreate(Bundle
savedInstanceState) {

super.onCreate(savedInstanceState);




setContentView(R.layout.activity_home6);

updateDate();




pauseButton = (Button) findViewById(R.id.pauseButton);

deleteButton = (Button) findViewById(R.id.deleteButton);

contactButton = (Button) findViewById(R.id.contactButton);

chartsButton = (Button) findViewById(R.id.chartsButton);

status_top = (TextView) findViewById(R.id.data_collection_textview);

status_bottom = (TextView) findViewById(R.id.data_collection_textview_bottom);




try {

getCatalogData();

} catch (JSONException e)
{

e.printStackTrace();

}




if (!systemStatusCheckerRunning) {

setSystemRequestUpdates();

}




}




@Override

public void onResume()
{

super.onResume();




if (isLayoutReady && isFirstRun)
{

updateBatteryLayout();

isFirstRun = false;

}

updateUI();

}




private void setSystemRequestUpdates()
{

final Handler systemRequestHandler
= new Handler();

Timer systemRequestTimer = new
Timer();

TimerTask systemRequestTimerTask = new
TimerTask() {

@Override

public void run()
{

systemRequestHandler.post(new
Runnable() {

@SuppressWarnings("unchecked")

public void run()
{

try {

requestSystemStatus();

requestBatteryStatus();

} catch (JSONException e)
{

e.printStackTrace();

}

}

});

}

};

systemRequestTimer.schedule(systemRequestTimerTask,
0, REQUEST_SYSTEM_STATUS_FREQUENCY);

systemStatusCheckerRunning = true;

}




private void requestBatteryStatus()
{

String tag_json_obj = "json_obj_req";




for (String key
: batteryObjects.keySet()) {




String url = BATTERY_STATUS_URL
+ "?uid=" + key;

Log.d("URL", url);




// Request a string response from the provided URL.

StringRequest stringRequest = new
StringRequest(Request.Method.GET,
url,

new Response.Listener<String>()
{

@Override

public void onResponse(String
response) {

updateBatteries(response);

}

}, new Response.ErrorListener()
{

@Override

public void onErrorResponse(VolleyError
error) {

Log.d("Error",
error.toString());

}

});




AppController.logToCurlRequest(stringRequest);




// Adding request to request queue

AppController.getInstance().addToRequestQueue(stringRequest,
tag_json_obj);

}

}




private void updateUI()
{




if (!isNetworkAvailable()) {

noNetworkUxUpdate();

Log.d("PAW", "No
network!");

}

else {

networkAvailableUxUpdate();

Log.d("PAW", "Network!");

}

}




private void networkAvailableUxUpdate()
{

pauseButton.setVisibility(View.VISIBLE);

deleteButton.setVisibility(View.VISIBLE);

contactButton.setVisibility(View.VISIBLE);

chartsButton.setVisibility(View.VISIBLE);




}




private void noNetworkUxUpdate()
{

pauseButton.setVisibility(View.INVISIBLE);

deleteButton.setVisibility(View.INVISIBLE);

contactButton.setVisibility(View.INVISIBLE);

chartsButton.setVisibility(View.INVISIBLE);




status_top.setText("Problems with WiFi, trying to
reconnect..");

status_top.setTextColor(getResources().getColor(R.color.errorRed));

}




private void updateBatteries(String
objString) {

try {




JSONObject messageObj = new
JSONObject(objString);







double batteryValue = messageObj.getJSONArray("e").getJSONObject(0).getDouble("v");
// value for battery




if (batteryValue > 4.5
|| batteryValue < 2.5) {

return;

}

//check if battery report is outdated (600sec = 10min) and if so assign it a value of -1

long delta = messageObj.getLong("bt")
- messageObj.getJSONObject("Date").getLong("sec");

if(delta >= 600){

batteryValue = -1;

}

Log.d("TimeDelta",
delta + "sec");




String batteryKey = messageObj.getString("uid");
// key




BatteryInfo bi = batteryObjects.get(batteryKey);




bi.setValue(batteryValue);




batteryObjects.put(batteryKey,
bi);




for (String key:
batteryObjects.keySet()) {




BatteryInfo bif = batteryObjects.get(key);




if (bif.getIndex()
== 0) {

TextView label0 = (TextView)
findViewById(R.id.label0);

label0.setText(bif.getLabel());

TextView battery0 = (TextView)
findViewById(R.id.battery0);




battery0.setBackgroundResource( 0
);

if (bif.getValue()
== 10.0 || bif.getValue() == -1)
{

battery0.setBackgroundResource(R.drawable.q_icon);

}

else if (bif.getValue()
>= 3.8) {

battery0.setBackgroundResource(R.drawable.battery_full_vertical);

}

else if (bif.getValue()
>= 3.7) {

battery0.setBackgroundResource(R.drawable.battery_half_vertical);

}

else if (bif.getValue()
>= 3.6) {

battery0.setBackgroundResource(R.drawable.battery_empty_vertical);

} else {

battery0.setBackgroundResource(R.drawable.battery_cempty_vertical);

}




battery0.setText("");

}




if (bif.getIndex()
== 1 && batteryObjects.size() > 1
) {

//Log.d("WEARABLE", "BIF = 1");

TextView label1 = (TextView)
findViewById(R.id.label1);

// Log.d("WEARABLE", "setText = " + bif.getLabel());

label1.setText(bif.getLabel());

TextView battery1 = (TextView)
findViewById(R.id.battery1);




if (bif.getValue()
== 10.0 || bif.getValue() == -1)
{

battery1.setBackgroundResource(R.drawable.q_icon);

}




else if (bif.getValue()
>= 3.8) {

battery1.setBackgroundResource(R.drawable.battery_full_vertical);

}

else if (bif.getValue()
>= 3.7) {

battery1.setBackgroundResource(R.drawable.battery_half_vertical);

}

else if (bif.getValue()
>= 3.6) {

battery1.setBackgroundResource(R.drawable.battery_empty_vertical);

} else {

battery1.setBackgroundResource(R.drawable.battery_cempty_vertical);

}

battery1.setText("");

}




if (bif.getIndex()
== 2 && batteryObjects.size() > 2
) {

TextView label2 = (TextView)
findViewById(R.id.label2);

label2.setText(bif.getLabel());

TextView battery2 = (TextView)
findViewById(R.id.battery2);




battery2.setBackgroundResource( 0
);

if (bif.getValue()
== 10.0 || bif.getValue() == -1)
{

battery2.setBackgroundResource(R.drawable.q_icon);

}

else if (bif.getValue()
>= 3.8) {

battery2.setBackgroundResource(R.drawable.battery_full_vertical);

}

else if (bif.getValue()
>= 3.7) {

battery2.setBackgroundResource(R.drawable.battery_half_vertical);

}

else if (bif.getValue()
>= 3.6) {

battery2.setBackgroundResource(R.drawable.battery_empty_vertical);

} else {

battery2.setBackgroundResource(R.drawable.battery_cempty_vertical);

}




battery2.setText("");

}

if (bif.getIndex()
== 3 && batteryObjects.size() > 3)
{

TextView label3 = (TextView)
findViewById(R.id.label3);

label3.setText(bif.getLabel());

TextView battery3 = (TextView)
findViewById(R.id.battery3);




battery3.setBackgroundResource( 0
);

if (bif.getValue()
== 10.0 || bif.getValue() == -1)
{

battery3.setBackgroundResource(R.drawable.q_icon);

}

else if (bif.getValue()
>= 3.8) {

battery3.setBackgroundResource(R.drawable.battery_full_vertical);

}

else if (bif.getValue()
>= 3.7) {

battery3.setBackgroundResource(R.drawable.battery_half_vertical);

}

else if (bif.getValue()
>= 3.6) {

battery3.setBackgroundResource(R.drawable.battery_empty_vertical);

} else {

battery3.setBackgroundResource(R.drawable.battery_cempty_vertical);

}

battery3.setText("");

}

if (bif.getIndex()
== 4 && batteryObjects.size() > 4)
{

TextView label4 = (TextView)
findViewById(R.id.label4);

label4.setText(bif.getLabel());

TextView battery4 = (TextView)
findViewById(R.id.battery4);




battery4.setBackgroundResource( 0
);

if (bif.getValue()
== 10.0 || bif.getValue() == -1)
{

battery4.setBackgroundResource(R.drawable.q_icon);

}

else if (bif.getValue()
>= 3.8) {

battery4.setBackgroundResource(R.drawable.battery_full_vertical);

}

else if (bif.getValue()
>= 3.7) {

battery4.setBackgroundResource(R.drawable.battery_half_vertical);

}

else if (bif.getValue()
>= 3.6) {

battery4.setBackgroundResource(R.drawable.battery_empty_vertical);

} else {

battery4.setBackgroundResource(R.drawable.battery_cempty_vertical);

}

battery4.setText("");

}

if (bif.getIndex()
== 5 && batteryObjects.size() > 5)
{

TextView label5 = (TextView)
findViewById(R.id.label5);

label5.setText(bif.getLabel());

TextView battery5 = (TextView)
findViewById(R.id.battery5);




battery5.setBackgroundResource( 0
);

if (bif.getValue()
== 10.0 || bif.getValue() == -1)
{

battery5.setBackgroundResource(R.drawable.q_icon);

}

else if (bif.getValue()
>= 3.8) {

battery5.setBackgroundResource(R.drawable.battery_full_vertical);

}

else if (bif.getValue()
>= 3.7) {

battery5.setBackgroundResource(R.drawable.battery_half_vertical);

}

else if (bif.getValue()
>= 3.6) {

battery5.setBackgroundResource(R.drawable.battery_empty_vertical);

} else {

battery5.setBackgroundResource(R.drawable.battery_cempty_vertical);

}

battery5.setText("");

}

}




} catch (JSONException e)
{

Log.d("LOG", "JSON
exception: " + e);

}

}




private void updateBatteryLayout()
{




// if (batteryInfo.size() == 1) {

// setContentView(R.layout.activity_home);

// }

// if (batteryInfo.size() == 2) {

// setContentView(R.layout.activity_home2);

// }

// if (batteryInfo.size() == 3) {

// setContentView(R.layout.activity_home3);

// }

// if (batteryInfo.size() == 4) {

// setContentView(R.layout.activity_home4);

// }




pauseButton = (Button) findViewById(R.id.pauseButton);

deleteButton = (Button) findViewById(R.id.deleteButton);

contactButton = (Button) findViewById(R.id.contactButton);

chartsButton = (Button) findViewById(R.id.chartsButton);

status_top = (TextView) findViewById(R.id.data_collection_textview);

status_bottom = (TextView) findViewById(R.id.data_collection_textview_bottom);




updateDate();

updateUI();




}




/**

*

* startRecording

* Publishes message to start recording data

*

*/

public void startRecording(View
v) {




status_top.setText("System status requested, awaiting
confirmation from the server..");

status_top.setTextColor(getResources().getColor(R.color.yellow));

status_bottom.setText("");




Log.d("TEST", "startRecording
pressed!");




String tag_json_obj = "json_obj_req";

String startRecording = "{\n"
+

"\t\"jsonrpc\": \"2.0\",\n" +

"\t\"method\": \"start\",\n" +

"\t\"params\": {\n" +

"\t\t\"delay\": 0,\n" +

"\t\t\"modality\": \"all\"\n" +

"\t},\n" +

"\t\"id\": \"index.php_863310\",\n" +

"\t\"dest\": \"node-red\",\n" +

"\t\"src\": \"web_wp6\"\n" +

"}";

try {

JSONObject obj = new
JSONObject(startRecording);

JsonObjectRequest jsonObjReq = new
JsonObjectRequest(Request.Method.POST,

START_RECORDING_URL, obj,

new Response.Listener<JSONObject>()
{

@Override

public void onResponse(JSONObject
response) {

try {

requestSystemStatus();

} catch (JSONException e)
{

e.printStackTrace();

}

}

}, new Response.ErrorListener()
{




@Override

public void onErrorResponse(VolleyError
error) {

VolleyLog.d("HYPERCUT",
"Error: " + error.getMessage());

}

}) {




@Override

public Map<String,
String> getHeaders() {

HashMap<String, String>
headers = new HashMap<>();

headers.put("Content-Type",
"application/json");




String credentials = "admin:erehps767";

String auth = "Basic "

+ Base64.encodeToString(credentials.getBytes(),
Base64.NO_WRAP);

headers.put("Authorization",
auth);




return headers;

}

};




AppController.logToCurlRequest(jsonObjReq);




// Adding request to request queue

AppController.getInstance().addToRequestQueue(jsonObjReq,
tag_json_obj);

} catch (JSONException e)
{

e.printStackTrace();

}

}




/**

*

* pauseRecording

* publishes message to pause recording for given time

* @param durationInt allowed values are:

* int 1 => 1h

* int 2 => today

* int 3 => forever

*

*/

public void pauseRecording(int
durationInt) {




status_top.setText("System status requested, awaiting
confirmation from the server..");

status_top.setTextColor(getResources().getColor(R.color.yellow));

status_bottom.setText("");




Log.d("TEST", "pauseRecording
called");

String tag_json_obj = "json_obj_req";

String duration = "";




switch (durationInt) {

case 1:

duration = "1h";

break;

case 2:

duration = "today";

break;

case 3:

duration = "forever";

break;

}




String stopRecording = "{\"jsonrpc\":\"2.0\",\"method\":\"pause\",\"params\":{\"delay\":0,
\"duration\": " +

"\"" + duration + "\" "
+

",\"modality\": \"all\"},\"id\":\"genie_12345\",\"dest\":\"node-red\",\"src\":\"genie\"}";




try {

JSONObject obj = new
JSONObject(stopRecording);

JsonObjectRequest jsonObjReq = new
JsonObjectRequest(Request.Method.POST,

START_RECORDING_URL, obj,

new Response.Listener<JSONObject>()
{

@Override

public void onResponse(JSONObject
response) {

try {

requestSystemStatus();

} catch (JSONException e)
{

e.printStackTrace();

}

}

}, new Response.ErrorListener()
{




@Override

public void onErrorResponse(VolleyError
error) {

VolleyLog.d("HYPERCUT",
"Error: " + error.getMessage());

}

}) {




@Override

public Map<String,
String> getHeaders() {

HashMap<String, String>
headers = new HashMap<>();

headers.put("Content-Type",
"application/json");




String credentials = "admin:erehps767";

String auth = "Basic "

+ Base64.encodeToString(credentials.getBytes(),
Base64.NO_WRAP);

headers.put("Authorization",
auth);







return headers;

}

};




AppController.logToCurlRequest(jsonObjReq);




// Adding request to request queue

AppController.getInstance().addToRequestQueue(jsonObjReq,
tag_json_obj);

} catch (JSONException e)
{

e.printStackTrace();

}







}




/**

*

* deleteHomeData

* publishes message to delete recorded data for @param durationInt time

* @param durationInt allowed values are:

* int 1 => 1 hour

* int 2 => 6 hours

* int 3 => 24 hours

*

*/

public void deleteHomeData(int
durationInt) {




status_top.setText("System status requested, awaiting
confirmation from the server..");

status_top.setTextColor(getResources().getColor(R.color.yellow));

status_bottom.setText("");




String tag_json_obj = "json_obj_req";

String duration = "";




switch (durationInt) {

case 1:

duration = "1";

break;

case 2:

duration = "6";

break;

case 3:

duration = "24";

break;

}




String deleteHomeData = "{\"jsonrpc\":\"2.0\",\"method\":\"delete\",\"params\":{\"duration\":
" +

duration +

", \"unit\": \"h\", \"modality\":\"all\"},\"id\":\"genie_12345\",\"dest\":\"node-red\",\"src\":\"genie\"}";




try {

JSONObject obj = new
JSONObject(deleteHomeData);

JsonObjectRequest jsonObjReq = new
JsonObjectRequest(Request.Method.POST,

START_RECORDING_URL, obj,

new Response.Listener<JSONObject>()
{

@Override

public void onResponse(JSONObject
response) {

try {

Log.d("PAWPAW",
response.toString());

requestSystemStatus();

//todo: WE NEED CONFIRMATION!!!!

Toast toast = Toast.makeText(getApplicationContext(),"Data
has been successfully deleted", Toast.LENGTH_LONG);

toast.setGravity(Gravity.TOP,
0, 100);

toast.show();

} catch (JSONException e)
{

e.printStackTrace();

}

}

}, new Response.ErrorListener()
{




@Override

public void onErrorResponse(VolleyError
error) {

VolleyLog.d("HYPERCUT",
"Error: " + error.getMessage());

}

}) {




@Override

public Map<String,
String> getHeaders() {

HashMap<String, String>
headers = new HashMap<>();

headers.put("Content-Type",
"application/json");




String credentials = "admin:erehps767";

String auth = "Basic "

+ Base64.encodeToString(credentials.getBytes(),
Base64.NO_WRAP);

headers.put("Authorization",
auth);




return headers;

}

};




AppController.logToCurlRequest(jsonObjReq);




// Adding request to request queue

AppController.getInstance().addToRequestQueue(jsonObjReq,
tag_json_obj);










//todo:

JsonObjectRequest secondRequest = new
JsonObjectRequest(Request.Method.GET,

DELETE_URL_TESTING, null,

new Response.Listener<JSONObject>()
{

@Override

public void onResponse(JSONObject
response) {

Log.d("PAWPAW",
response.toString());

}

}, new Response.ErrorListener()
{




@Override

public void onErrorResponse(VolleyError
error) {

VolleyLog.d("PAWPAW",
"Error: " + error.getMessage());

}

}) {




@Override

public Map<String,
String> getHeaders() {

HashMap<String, String>
headers = new HashMap<>();

headers.put("Content-Type",
"application/json");




String credentials = "admin:erehps767";

String auth = "Basic "

+ Base64.encodeToString(credentials.getBytes(),
Base64.NO_WRAP);

headers.put("Authorization",
auth);




return headers;

}

};




AppController.logToCurlRequest(jsonObjReq);




// Adding request to request queue

AppController.getInstance().addToRequestQueue(secondRequest,
tag_json_obj);










} catch (JSONException e)
{

e.printStackTrace();

}

}




/**

*

* requestSystemStatus

* Publishes message to request current system status_top

*

*/

public void requestSystemStatus()
throws JSONException {

Log.d("PAW", "requestSystemStatus
called");

status_top.setText("System status requested, awaiting
confirmation from the server..");

status_top.setTextColor(getResources().getColor(R.color.yellow));

status_bottom.setText("");




String tag_json_obj = "json_obj_req";




//JSONObject obj = new JSONObject(systemStatusRequest);




JsonObjectRequest jsonObjReq = new
JsonObjectRequest(Request.Method.GET,

SYSTEM_STATUS_URL, null,

new Response.Listener<JSONObject>()
{

@Override

public void onResponse(JSONObject
response) {

String pausedUntil = "";

Log.d("TEST", response.toString());







try {




if (response.has("stoppedFor")
&& response.getLong("stoppedFor") == -1)
{

updateSystemStatus(false, -1);

return;

}




else if (!response.getBoolean("stopped"))
{

//system is running

updateSystemStatus(true, 0);







}







else {

long epoch = response.getJSONObject("stoppedUntil").getLong("sec")
* 1000;




updateSystemStatus(false, epoch);

}

}catch (JSONException e)
{

e.printStackTrace();

}

}

}, new Response.ErrorListener()
{




@Override

public void onErrorResponse(VolleyError
error) {

VolleyLog.d("HYPERCUT",
"Error: " + error.getMessage());

}

}) {




@Override

public Map<String,
String> getHeaders() {

HashMap<String, String>
headers = new HashMap<>();

headers.put("Content-Type",
"application/json");

return headers;

}

};




AppController.logToCurlRequest(jsonObjReq);




// Adding request to request queue

AppController.getInstance().addToRequestQueue(jsonObjReq,
tag_json_obj);

}




/**

*

* updateSystemStatus

* @param isRecording boolean to indicate if system is currently recording

* @param pausedUntil string with date when system will start recording again

*

*/

public void updateSystemStatus(Boolean
isRecording, long pausedUntil)
{




String pausedText = "";




if (pausedUntil == -1)
{

pausedText = "System pasued indefinitely\n";

status_top.setText("");

status_bottom.setText(pausedText
+ "Press here to resume");

status_bottom.setTextColor(getResources().getColor(R.color.errorRed));

return;

}




SimpleDateFormat formatter = new
SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSS'Z'");

formatter.setTimeZone(TimeZone.getTimeZone("GMT"));




SimpleDateFormat bstFormatter = new
SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSS'Z'");

bstFormatter.setTimeZone(TimeZone.getTimeZone("BST"));




try {

//Date dateStr = formatter.parse(pausedUntil);




Date dateStr = new
Date(pausedUntil);




String oldDate = formatter.format(dateStr);




Date newDate = bstFormatter.parse(oldDate);




String dateStrMinutes = ""
+ dateStr.getMinutes();

String dateStrHours = ""
+ dateStr.getHours();

if (Integer.parseInt(dateStrMinutes)
< 10) {

dateStrMinutes = "0" + dateStrMinutes;

}

if (Integer.parseInt(dateStrHours)
< 10) {

dateStrHours = "0" + dateStrHours;

}




pausedText = "System paused until " + dateStrHours
+ ":" + dateStrMinutes + "\n";

} catch (ParseException e)
{

e.printStackTrace();

pausedText = "System pasued indefinitely\n";

}




if (isRecording) {

status_top.setText("");

status_bottom.setText("Recording!");

status_bottom.setTextColor(getResources().getColor(R.color.greenAccept));

}

else {

status_top.setText("");

status_bottom.setText(pausedText
+ "Press here to resume");

status_bottom.setTextColor(getResources().getColor(R.color.errorRed));

}

}




/**

*

* updateDate

* updates date on the dashboard

*

*/

private void updateDate()
{

String formattedDate = new
SimpleDateFormat("EEEE, dd MMMMMMM", Locale.UK).format(new
Date());

TextView currentDate = (TextView)
findViewById(R.id.date_textview);

assert currentDate != null;

currentDate.setText(formattedDate);




}




public void showPauseDialog(
View v) {

status_top.setText("Your instruction has been sent,
awaiting confirmation from the server..");

status_top.setTextColor(getResources().getColor(R.color.yellow));

Intent i = new
Intent(this, ConfirmationDialogActivity.class);

i.putExtra("isPause",
"true");

startActivityForResult(i, 1);




}




public void showDeleteDialog(
View v) {

status_top.setText("Your instruction has been sent,
awaiting confirmation from the server..");

status_top.setTextColor(getResources().getColor(R.color.yellow));

Intent i = new
Intent(this, ConfirmationDialogActivity.class);

i.putExtra("isPause",
"false");

startActivityForResult(i, 1);




}




public void showContactDialog(
View v) {

Log.d("Paw", "Contact
clicked!");




//Enables messaging view

// Intent i = new Intent(this, ContactUsDialogActivity.class);

// startActivity(i);

}




@Override

protected void onActivityResult(int
requestCode, int resultCode, Intent
data) {

// PAUSE DIALOG

if (requestCode == 1)
{

// Make sure the request was successful

if (resultCode == RESULT_OK)
{

String isPause = data.getExtras().getString("isPause");

int selectedButton = data.getExtras().getInt("selectedButton");




if (isPause.equals("pause"))
{

pauseRecording(selectedButton);

}




if (isPause.equals("delete"))
{

deleteHomeData(selectedButton);

}




}

}

}




public void getCatalogData()
throws JSONException {

String tag_json_obj = "json_obj_req";

Log.d("HYPERCAT",
"calling getCatalogData");




// final ProgressDialog pDialog = new ProgressDialog(this);

// pDialog.setMessage("Getting layout...");

// pDialog.show();

String url = CAT_URL
+ ":8001/cat?val=SPW2";




JsonObjectRequest jsonObjReq = new
JsonObjectRequest(Request.Method.GET,

url, null,

new Response.Listener<JSONObject>()
{




@Override

public void onResponse(JSONObject
response) {




try {

for (int i
= 0; i < response.getJSONArray("items").length();
i++) {




String key = response.getJSONArray("items").getJSONObject(i).getString("href");




if (!key.contains(":"))
{

key = key.substring(0,2)
+ ":" + key.substring(2,4)
+ ":" + key.substring(4,6)
+ ":" + key.substring(6,8)
+ ":"

+ key.substring(8,10)
+ ":" + key.substring(10,12);




}




batteryInfo.put(key,
response.getJSONArray("items").getJSONObject(i).getJSONArray("i-object-metadata").getJSONObject(2).getString("val"));

BatteryInfo newBattery = new
BatteryInfo(i, key, response.getJSONArray("items").getJSONObject(i).getJSONArray("i-object-metadata").getJSONObject(2).getString("val"));

batteryObjects.put(key,
newBattery);

//

}

Log.d("PRETTY MAP",
batteryInfo.toString());

Log.d("HYPERCAT",
batteryObjects.toString());

isLayoutReady = true;




} catch (JSONException e)
{

e.printStackTrace();

}




}

}, new Response.ErrorListener()
{




@Override

public void onErrorResponse(VolleyError
error) {

VolleyLog.d("HYPERCUT",
"Error: " + error.getMessage());

// pDialog.hide();

}

}) {




@Override

public Map<String,
String> getHeaders() {

HashMap<String, String>
headers = new HashMap<>();

headers.put("Content-Type",
"application/json");

return headers;

}

};




AppController.logToCurlRequest(jsonObjReq);




// Adding request to request queue

AppController.getInstance().addToRequestQueue(jsonObjReq,
tag_json_obj);

}




private boolean isNetworkAvailable()
{

ConnectivityManager connectivityManager

= (ConnectivityManager) getSystemService(Context.CONNECTIVITY_SERVICE);

NetworkInfo activeNetworkInfo = connectivityManager.getActiveNetworkInfo();

return activeNetworkInfo != null
&& activeNetworkInfo.isConnected();

}

}
