
import pandas as pd

def run_pipeline(args, tracker) -> None:
    
    input_path = args.dataset

    df = pd.read_csv(input_path)

    # Sample or replicate the dataframe based on the fraction argument
    if args.frac > 0.0 and args.frac < 1.0:
        df = df.sample(frac=args.frac)
    elif args.frac > 1.0:
        df = pd.concat([df] * int(args.frac), ignore_index=True)

    # Subscribe dataframe
    df = tracker.subscribe(df)
    tracker.analyze_changes(df)

    # Clean and format car price and mileage columns
    columns = ['car_price', 'car_mileage']
    for col in columns:
        df[col] = df[col].apply(lambda x: '{:.1f}k'.format(x / 1000) if x >= 1000 else x)
    tracker.analyze_changes(df)

    # Drop unnecessary columns
    df = df.drop(['car_transmission', 'car_drive', 'car_engine_capacity', 'car_engine_hp'], axis=1)
    tracker.analyze_changes(df)

    # Rename the first column to 'car_id'
    df.rename(columns={df.columns[0]: 'car_id'}, inplace=True)
    tracker.analyze_changes(df)

    # Strip whitespace from car brand, model, and city columns
    cols = ['car_brand', 'car_model', 'car_city']
    df[cols] = df[cols].applymap(str.strip)
    tracker.analyze_changes(df)

    # Create a new column 'car_age_category' based on the 'car_age' column
    df['car_age_category'] = df['car_age'].apply(lambda age: 'New' if age <= 3 else ('Middle' if age <= 9 else 'Old'))
    tracker.analyze_changes(df)
