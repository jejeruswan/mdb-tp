import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, Image, Dimensions } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { BlurView } from 'expo-blur';
import MapView, { Marker, PROVIDER_GOOGLE } from 'react-native-maps';
import { useRouter } from 'expo-router';
import { theme } from '@/constants/theme';
import { Event, EventCategory, CATEGORIES, DEFAULT_EVENT_IMAGE } from '../../types';
import { supabase } from '../../services/supabase';
import { SearchBar } from '../../components/SearchBar';

const { width, height } = Dimensions.get('window');

// Berkeley coordinates
const BERKELEY_REGION = {
  latitude: 37.8719,
  longitude: -122.2585,
  latitudeDelta: 0.05,
  longitudeDelta: 0.05,
};

export default function MapScreen() {
  const router = useRouter();
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<EventCategory | 'top' | null>('top');
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchEvents();
  }, []);

  const fetchEvents = async () => {
    try {
      const { data, error } = await supabase
        .from('events')
        .select('*')
        .order('created_at', { ascending: false });

      if (error) throw error;

      if (data) {
        // Add random coordinates near Berkeley for demo
        // In production, you'd parse actual locations or use geocoding
        const eventsWithCoords = data.map((event, index) => ({
          ...event,
          latitude: event.latitude || BERKELEY_REGION.latitude + (Math.random() - 0.5) * 0.02,
          longitude: event.longitude || BERKELEY_REGION.longitude + (Math.random() - 0.5) * 0.02,
        }));
        setEvents(eventsWithCoords);
      }
    } catch (error) {
      console.error('Error fetching events:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCategoryPress = (category: EventCategory | 'top') => {
    setSelectedCategory(selectedCategory === category ? null : category);
  };

  const handleMarkerPress = (event: Event) => {
    router.push({
      pathname: '/event/[id]',
      params: { id: event.id, eventData: JSON.stringify(event) },
    });
  };

  // Filter events
  const filteredEvents = events.filter((event) => {
    const matchesSearch = searchQuery
      ? event.title.toLowerCase().includes(searchQuery.toLowerCase())
      : true;

    const matchesCategory = selectedCategory && selectedCategory !== 'top'
      ? event.category === selectedCategory
      : true;

    return matchesSearch && matchesCategory;
  });

  // Get top events (most recent 10)
  const displayEvents = selectedCategory === 'top' 
    ? filteredEvents.slice(0, 10)
    : filteredEvents;

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      {/* Map */}
      <MapView
        style={styles.map}
        provider={PROVIDER_GOOGLE}
        initialRegion={BERKELEY_REGION}
        showsUserLocation
        showsMyLocationButton
      >
        {displayEvents.map((event) => (
          <Marker
            key={event.id}
            coordinate={{
              latitude: event.latitude || BERKELEY_REGION.latitude,
              longitude: event.longitude || BERKELEY_REGION.longitude,
            }}
            onPress={() => handleMarkerPress(event)}
          >
            <View style={styles.markerContainer}>
              <Image
                source={{ uri: event.image_url || DEFAULT_EVENT_IMAGE }}
                style={styles.markerImage}
              />
            </View>
          </Marker>
        ))}
      </MapView>

      {/* Bottom Controls */}
      <View style={styles.bottomControls}>
        {/* Category Filter with Blur Background */}
        <View style={styles.categoryContainer}>
          <BlurView intensity={80} tint="light" style={styles.blurContainer}>
            <View style={styles.blurOverlay} />
            <ScrollView
              horizontal
              showsHorizontalScrollIndicator={false}
              contentContainerStyle={styles.categoryList}
              style={styles.categoryScroll}
            >
              {/* Top category */}
              <TouchableOpacity
                style={[
                  styles.categoryChip,
                  selectedCategory === 'top' && styles.categoryChipSelected,
                ]}
                onPress={() => handleCategoryPress('top')}
              >
                <Text style={styles.categoryEmoji}>⭐</Text>
                <Text style={[
                  styles.categoryLabel,
                  selectedCategory === 'top' && styles.categoryLabelSelected,
                ]}>
                  top
                </Text>
              </TouchableOpacity>

              {/* Regular categories */}
              {CATEGORIES.map((category) => (
                <TouchableOpacity
                  key={category.id}
                  style={[
                    styles.categoryChip,
                    selectedCategory === category.id && styles.categoryChipSelected,
                  ]}
                  onPress={() => handleCategoryPress(category.id)}
                >
                  <Text style={styles.categoryEmoji}>{category.emoji}</Text>
                  <Text style={[
                    styles.categoryLabel,
                    selectedCategory === category.id && styles.categoryLabelSelected,
                  ]}>
                    {category.label}
                  </Text>
                </TouchableOpacity>
              ))}
            </ScrollView>
          </BlurView>
        </View>

        {/* Search Bar */}
        <View style={styles.searchContainer}>
          <SearchBar
            value={searchQuery}
            onChangeText={setSearchQuery}
            placeholder="recruitment"
          />
        </View>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  map: {
    width: width,
    height: height,
  },
  markerContainer: {
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: theme.colors.white,
    padding: 3,
    ...theme.shadows.md,
  },
  markerImage: {
    width: 44,
    height: 44,
    borderRadius: 22,
  },
  bottomControls: {
    position: 'absolute',
    bottom: 100, // Above tab bar
    left: 0,
    right: 0,
  },
  categoryContainer: {
    marginHorizontal: theme.spacing.lg,
    marginBottom: theme.spacing.md,
    borderRadius: theme.borderRadius.xl,
    overflow: 'hidden',
  },
  blurContainer: {
    borderRadius: theme.borderRadius.xl,
    overflow: 'hidden',
  },
  blurOverlay: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: 'rgba(255, 255, 255, 0.3)',
  },
  categoryScroll: {
    paddingVertical: theme.spacing.md,
  },
  categoryList: {
    paddingHorizontal: theme.spacing.lg,
    flexDirection: 'row',
    gap: theme.spacing.sm,
  },
  categoryChip: {
    flexDirection: 'column',
    alignItems: 'center',
    paddingHorizontal: theme.spacing.md,
    paddingVertical: theme.spacing.sm,
    borderRadius: theme.borderRadius.md,
    backgroundColor: 'rgba(255, 255, 255, 0.6)',
    marginRight: theme.spacing.sm,
    minWidth: 60,
  },
  categoryChipSelected: {
    backgroundColor: theme.colors.primary,
  },
  categoryEmoji: {
    fontSize: 24,
    marginBottom: theme.spacing.xs,
  },
  categoryLabel: {
    fontSize: theme.fontSize.xs,
    fontFamily: 'Inter_500Medium',
    color: theme.colors.textPrimary,
  },
  categoryLabelSelected: {
    color: theme.colors.white,
  },
  searchContainer: {
    paddingHorizontal: 0,
  },
});