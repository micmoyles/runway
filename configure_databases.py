'''create table outages (messageCreationTs timestamp, AffectedUnitEIC varchar(30), AssetType varchar(30), AffectedUnit varchar(30), DurationUncertainty varchar(30), RelatedInformation varchar(200), AssetId varchar(30), EventType varchar(30), NormalCapacity float(10,5), AvailableCapacity float(10,5), EventStatus varchar(30), EventStart timestamp, EventEnd timestamp, Cause varchar(30), FuelType varchar(30), Participant_MarketParticipantID varchar(30), MessageHeading varchar(30) )'''
'''
 create table plant_status ( AssetID varchar(30), Status varchar(30), NormalCapacity float(10,5), CurrentCapacity float(10,5));
'''
'''
create table Plants ( name varchar(30), AssetID varchar(30), FuelType varchar(30), NormalCapacity float(10,5), plantID int not null auto_increment, primary key (plantID) )
'''

