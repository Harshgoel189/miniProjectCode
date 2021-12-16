Map.setCenter(77.64,27.56,10)
var shp=ee.FeatureCollection(boundary);
Map.addLayer(shp,{},'polygon');
var selection=L8.filterBounds(ROI)
.filterDate("2020-01-01",'2021-10-07')
.filterMetadata("CLOUD_COVER","less_than",5)
.mean()
.clip(ROI)
Map.addLayer(selection,{bands:["B4","B3","B2"]})
var training_points=Water.merge(Urbanisation).merge(Forest).merge(Barren_land).merge(Agriculture);
print(training_points)
var training_data=selection.sampleRegions({
                    collection:training_points,
                    properties:['LC'],
                    scale:30})
var classifier=ee.Classifier.smileRandomForest(20)
var classifier=classifier.train({features:
                              training_data,
                              classProperty:"LC",
                              inputProperties:["B1","B2","B3","B4","B5","B6","B7","B10","B11"]});
var classified_image=selection.classify(classifier);
Map.addLayer(classified_image,{min:0,max:4,palette:['blue','red','green','brown','yellow']},'classified image');
print(classifier.confusionMatrix())
var withRandom =training_data.randomColumn('random');
var split=0.7
var trainingPartition=withRandom.filter(ee.Filter.lt('random',split));
var testingPartition=withRandom.filter(ee.Filter.gte('random',split));
var trainedClassifier=ee.Classifier.smileRandomForest(20).train({
  features:trainingPartition,
  classProperty:'LC',
  inputProperties:selection.bandNames()
});
var test_1=testingPartition.classify(trainedClassifier);
var confusionMatrix_2001=test_1.errorMatrix('LC','classification');
print('confusionMatrix_2001',confusionMatrix_2001);
print('validation overall accuracy',confusionMatrix_2001.accuracy());
print('kappa cofficient',confusionMatrix_2001.kappa());

var Water=classified_image.select('classification').eq(0);
var urban=classified_image.select('classification').eq(1);
var forest=classified_image.select('classification').eq(2);
var barren_land=classified_image.select('classification').eq(3);
var Agriculture=classified_image.select('classification').eq(4);

//Finding area of roi....
var area_water=Water.multiply(ee.Image.pixelArea()).divide(10000);
var area_urban=urban.multiply(ee.Image.pixelArea()).divide(10000);
var area_agri=Agriculture.multiply(ee.Image.pixelArea()).divide(10000);
var area_forest=forest.multiply(ee.Image.pixelArea()).divide(10000);
var area_barren=barren_land.multiply(ee.Image.pixelArea()).divide(10000);

//print("Area of water : ",area_water);

//reducing the stastistical area
var stat1=area_water.reduceRegion({
  reducer:ee.Reducer.sum(),
  geometry:ROI,
  scale:10,
  maxPixels:1e9
});

var stat2=area_urban.reduceRegion({
  reducer:ee.Reducer.sum(),
  geometry:ROI,
  scale:10,
  maxPixels:1e9
});

var stat3=area_barren.reduceRegion({
  reducer:ee.Reducer.sum(),
  geometry:ROI,
  scale:10,
  maxPixels:1e9
});

var stat4=area_agri.reduceRegion({
  reducer:ee.Reducer.sum(),
  geometry:ROI,
  scale:10,
  maxPixels:1e9
});

var stat5=area_forest.reduceRegion({
  reducer:ee.Reducer.sum(),
  geometry:ROI,
  scale:10,
  maxPixels:1e9
});


print("Area of water in ha: ",stat1);
print("Area of urban in ha: ",stat2);
print("Area of barrenLand in ha: ",stat3);
print("Area of agriculture in ha: ",stat4);
print("Area of forest in ha: ",stat5);

Map.add(ui.Label( 
    '2020 Land Cover Map of Vrindavan_Mathura',  { 
      fontWeight: 'bold', BackgroundColor: 'FBF9F5',fontSize: '20px'})); 
       
// Names of land features to be added in Legends palette 
var names = [ 'Water','Urbanisation','Forest', 'Barren_Land','Agriculture' ]; 
 
var values = [ '0', '1', '2','3','4' ]; //values of land features 
     
var legendsPalette = ['1728ff','ff0000','23841d', 'd7a376','eef855']; //color codes of land features 
 
// Adding title of the panel 
var legendTitle = ui.Label({value: 'Land Cover Legends ',style: { 
  fontWeight: 'bold', fontSize: '30px', margin: '0 0 6px 0', padding: '0' }}); 
 
// positioning of panel on the map 
var legend = ui.Panel({style: { position: 'bottom-left', padding: '8px 15px'}}); 
  
  
// Adding the Title on the panel 
legend.add(legendTitle); 
  
var makeRow = function(color, name) { // This function will return the colors and names of features 
  // Label of the colored box in the panel 
  var colorBox = ui.Label({ 
    style: { 
      backgroundColor: '#' + color, padding: '8px',margin: '0 0 4px 0'} }); 
 
  // Label of the name written against the color(name of land feature) 
  var description = ui.Label({ 
    value: name, style: {margin: '0 0 4px 6px'}}); 
 
  // returning the panel to the makerow function 
  return ui.Panel({ 
    widgets: [colorBox, description],layout: ui.Panel.Layout.Flow('horizontal')})}; 
  
// Add color and and names to the panel 
for (var i = 0; i < 5; i++) { 
  legend.add(makeRow(legendsPalette[i], names[i]));  // It will call the makerow function to get the color and names of lands features 
  }   
 
// Finally adding the panel to the map 
Map.add(legend);
