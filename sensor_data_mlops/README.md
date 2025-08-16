# Dagster Project Structure
## Definitions
Definitions describe what is contained in the Dagster project. `definitions.py` is a top level file needed by dagster to detect assets, resources, and sensors. A Dagster code location must contain `definitions.py`.
## Assets
Assets represent anything which can be materialized to a filesystem or database. Assets are the foundation of Dagster. Functions are defined as assets using `@dg.asset()`. Assets are contained in the `assets.py` file
## Jobs
Jobs are used to run specific assets. The `dg.define_asset_job()` method is used to create jobs. Jobs are contained in the `jobs.py` file.
## Sensors
Sensors are used to automatically run jobs in response to defined triggers. Sensors are defined by placing `@dg.sensor()` above a function, which can also be used to dictate whether the sensor runs on project launch and how frequently the sensor should run. Sensors are contained in the `sensors.py` file.
## Resources
Resources can be databases, storage buckets, or any other dependency used by assets and sensors. Resources are contained in the `resources.py` file.
## Constants
Constants represent paths or other string and numerical data shared among sensors and assets. Constants are contained in the `constants.py` file

## Environment variables
Dagster has a proprietary method of handling environment variables, `dg.EnvVar()`. Environment variables may be defined in docker or using a `.env` file. This is useful for handling secrets.

# Other Project Files
Functions which do not fall under a Dagster classification are contained within the `utils.py` file.

The file `model.py` is derived from **Transformer-based Models to Deal with Heterogeneous Environments in Human Activity Recognition** [[Paper](https://link.springer.com/article/10.1007/s00779-023-01776-3)] by *[Sannara Ek](https://sannaraek.github.io/), [François Portet](https://lig-membres.imag.fr/portet/home.php), [Philippe Lalanda](https://lig-membres.imag.fr/lalanda/)*. The repository is available [here](https://github.com/getalp/Lightweight-Transformer-Models-For-HAR-on-Mobile-Devices). The model is a transformer specifically designed for IMU data. 

Resources may be defined as a separate class and then added to project definition using the `resources.py` file. The class used for handling Google Drive integration is included in the `filestorebucket.py` file.

Dependencies are contained in the `pyproject.toml` file, along with specific project settings.
