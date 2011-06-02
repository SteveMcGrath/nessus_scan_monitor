%if len(active_hosts) > 0:
<p>The Following IPs are currently being scanned:</p>
<table>
  <tr>
    <th width="150" bgcolor="#6D7B8D">Address</th>
    <th width="150" bgcolor="#6D7B8D">Time Started</th>
    <th width="150" bgcolor="#6D7B8D">Duration (Seconds)</th>
  </tr>
%for host in active_hosts:
  <tr>
    <td align="center">{{host['address']}}</td>
    <td align="center">{{host['started']}}</td>
    <td align="right">{{host['duration']}}</td>
  </tr>
%end
</table>
%end
<table>
  <form action="/" method="POST">
  <tr>
    <td>IP Lookup :</td>
    <td><input type="text" size="16" maxlength="16" name="address" /></td>
    <td><input type="submit" name="lookup" value="lookup"></td>
  </tr>
  </form>
</table>
%if searched:
<table>
  <tr>
    <th width="150" bgcolor="#6D7B8D">Address</th>
    <th width="150" bgcolor="#6D7B8D">Time Started</th>
    <th width="150" bgcolor="#6D7B8D">Time Stopped</th>
    <th width="150" bgcolor="#6D7B8D">Duration (Seconds)</th>
  </tr>
  %for host in search_hosts:
    <tr>
      <td>{{host.address}}</td>
      <td align="center">{{host.started.strftime('%D %H:%M')}}</td>
      <td align="center">{{host.stopped.strftime('%D %H:%M')}}</td>
      <td align="right">{{host.duration}}</td></tr>
  %end
</table>
%end