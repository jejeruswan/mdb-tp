import React from 'react';
import {
  View,
  Text,
  Image,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Linking,
  Dimensions,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { theme } from '@/constants/theme';
import { Event, DEFAULT_EVENT_IMAGE, CATEGORIES } from '../../types';

const { width } = Dimensions.get('window');

export default function EventDetailScreen() {
  const router = useRouter();
  const params = useLocalSearchParams();
  
  // Parse event data from params
  const event: Event = params.eventData ? JSON.parse(params.eventData as string) : null;

  if (!event) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.errorContainer}>
          <Text style={styles.errorText}>Event not found</Text>
        </View>
      </SafeAreaView>
    );
  }

  const imageUrl = event.image_url || DEFAULT_EVENT_IMAGE;

  // Get category emoji
  const categoryData = CATEGORIES.find(cat => cat.id === event.category);
  const categoryEmoji = categoryData?.emoji || '📚';

  const handleOpenLink = () => {
    if (event.source_url) {
      Linking.openURL(event.source_url);
    }
  };

  return (
    <View style={styles.container}>
      <ScrollView showsVerticalScrollIndicator={false}>
        {/* Header with Back Button */}
        <View style={styles.header}>
          <TouchableOpacity
            style={styles.backButton}
            onPress={() => router.push('/(tabs)')}
          >
            <Ionicons name="chevron-back" size={28} color={theme.colors.primary} />
          </TouchableOpacity>
        </View>

        {/* Event Image with Category Badges */}
        <View style={styles.imageWrapper}>
          <Image
            source={{ uri: imageUrl }}
            style={styles.image}
            resizeMode="cover"
          />
          {/* Category Badges on Image */}
          <View style={styles.categoryBadges}>
            <View style={styles.categoryBadge}>
              <Text style={styles.badgeEmoji}>{categoryEmoji}</Text>
              <Text style={styles.badgeText}>{event.category}</Text>
            </View>
            {event.club_name && (
              <View style={styles.categoryBadge}>
                <Ionicons name="briefcase" size={16} color={theme.colors.white} />
                <Text style={styles.badgeText}>work</Text>
              </View>
            )}
          </View>
        </View>

        {/* Content */}
        <View style={styles.content}>
          {/* Title and Avatars */}
          <View style={styles.titleSection}>
            <Text style={styles.title}>{event.title}</Text>
            {/* Mock avatars */}
            <View style={styles.avatars}>
              <Image
                source={{ uri: 'https://i.pravatar.cc/100?img=1' }}
                style={[styles.avatar, styles.avatar1]}
              />
              <Image
                source={{ uri: 'https://i.pravatar.cc/100?img=2' }}
                style={[styles.avatar, styles.avatar2]}
              />
              <Image
                source={{ uri: 'https://i.pravatar.cc/100?img=3' }}
                style={[styles.avatar, styles.avatar3]}
              />
            </View>
          </View>

          {/* Location */}
          <View style={styles.locationRow}>
            <Ionicons name="location" size={18} color={theme.colors.primary} />
            <Text style={styles.locationText}>{event.location || 'TKS'}</Text>
          </View>

          {/* Tagline */}
          {event.club_name && (
            <Text style={styles.tagline}>{event.club_name}</Text>
          )}

          {/* Description */}
          {event.description && (
            <Text style={styles.description}>{event.description}</Text>
          )}

          {/* Optional: View Source Button */}
          {event.source_url && (
            <TouchableOpacity style={styles.sourceButton} onPress={handleOpenLink}>
              <Text style={styles.sourceButtonText}>View Original Event</Text>
              <Ionicons name="open-outline" size={18} color={theme.colors.primary} />
            </TouchableOpacity>
          )}
        </View>

        {/* Bottom padding for tab bar */}
        <View style={{ height: 120 }} />
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  errorText: {
    fontSize: theme.fontSize.base,
    fontFamily: 'Inter_400Regular',
    color: theme.colors.textSecondary,
  },
  header: {
    paddingHorizontal: theme.spacing.lg,
    paddingTop: theme.spacing.xl,
    paddingBottom: theme.spacing.md,
  },
  backButton: {
    width: 40,
    height: 40,
    justifyContent: 'center',
  },
  imageWrapper: {
    width: width - 32,
    height: 280,
    marginHorizontal: theme.spacing.lg,
    borderRadius: theme.borderRadius.xl,
    overflow: 'hidden',
    position: 'relative',
  },
  image: {
    width: '100%',
    height: '100%',
  },
  categoryBadges: {
    position: 'absolute',
    bottom: theme.spacing.lg,
    left: theme.spacing.md,
    flexDirection: 'row',
    gap: theme.spacing.sm,
  },
  categoryBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: theme.colors.primary,
    paddingHorizontal: theme.spacing.md,
    paddingVertical: theme.spacing.sm,
    borderRadius: theme.borderRadius.full,
    gap: theme.spacing.xs,
  },
  badgeEmoji: {
    fontSize: 14,
  },
  badgeText: {
    fontSize: theme.fontSize.sm,
    fontFamily: 'Inter_600SemiBold',
    color: theme.colors.white,
  },
  content: {
    padding: theme.spacing.xl,
  },
  titleSection: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: theme.spacing.md,
  },
  title: {
    flex: 1,
    fontSize: theme.fontSize.xxxl,
    fontFamily: 'Inter_700Bold',
    color: theme.colors.textPrimary,
    textTransform: 'uppercase',
  },
  avatars: {
    flexDirection: 'row',
    marginLeft: theme.spacing.md,
  },
  avatar: {
    width: 32,
    height: 32,
    borderRadius: 16,
    borderWidth: 2,
    borderColor: theme.colors.white,
  },
  avatar1: {
    zIndex: 3,
  },
  avatar2: {
    marginLeft: -8,
    zIndex: 2,
  },
  avatar3: {
    marginLeft: -8,
    zIndex: 1,
  },
  locationRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: theme.spacing.md,
  },
  locationText: {
    fontSize: theme.fontSize.base,
    fontFamily: 'Inter_500Medium',
    color: theme.colors.textPrimary,
    marginLeft: theme.spacing.xs,
  },
  tagline: {
    fontSize: theme.fontSize.base,
    fontFamily: 'Inter_600SemiBold',
    color: theme.colors.textPrimary,
    marginBottom: theme.spacing.lg,
  },
  description: {
    fontSize: theme.fontSize.base,
    fontFamily: 'Inter_400Regular',
    color: theme.colors.textSecondary,
    lineHeight: 24,
    marginBottom: theme.spacing.xl,
  },
  sourceButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: theme.spacing.md,
    paddingHorizontal: theme.spacing.xl,
    borderWidth: 1,
    borderColor: theme.colors.primary,
    borderRadius: theme.borderRadius.md,
    gap: theme.spacing.sm,
  },
  sourceButtonText: {
    fontSize: theme.fontSize.base,
    fontFamily: 'Inter_600SemiBold',
    color: theme.colors.primary,
  },
});